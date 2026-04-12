import argparse
import json
import logging
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def setup_logger(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("orc_outcome")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def parse_iso(value: str | None):
    if not value:
        return None

    value = value.strip()

    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    raise ValueError(f"Unsupported ISO datetime format: {value}")


def duration_seconds(start: str | None, end: str | None):
    s = parse_iso(start)
    e = parse_iso(end)
    if not s or not e:
        return None
    return int((e - s).total_seconds())


def load_json(path: Path, logger: logging.Logger) -> dict:
    logger.debug(f"Loading JSON: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_outline(data: dict) -> dict:
    return data.get("dfir-orc", {}).get("outline", {})


def get_outcome(data: dict) -> dict:
    return data.get("dfir-orc", {}).get("outcome", {})


def status_code(status: str) -> int:
    return {"ok": 0, "warning": 1, "error": 2}.get(status, 2)


def normalize_filename(name: str, computer_name: str) -> str:
    if not name:
        return ""
    return (
        name.replace("{FullComputerName}", computer_name)
        .replace("{ComputerName}", computer_name)
        .lower()
    )


def strip_p7b(name: str) -> str:
    return re.sub(r"\.p7b$", "", name or "", flags=re.IGNORECASE)


def parse_size_to_bytes(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)

    text = str(value).strip()
    if not text or text.upper() == "N/A":
        return None

    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([KMGTP]?B)?\s*$", text, flags=re.IGNORECASE)
    if not m:
        return None

    number = float(m.group(1))
    unit = (m.group(2) or "B").upper()

    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "PB": 1024**5,
    }
    return int(number * multipliers[unit])


def find_single_json(run_dir: Path, kind: str, logger: logging.Logger) -> Path:
    matches = sorted(run_dir.glob(f"DFIR-ORC-{kind}_*.json"))
    logger.debug(f"Looking for DFIR-ORC-{kind}_*.json in {run_dir}: found {len(matches)}")
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one DFIR-ORC-{kind}_*.json in {run_dir}, found {len(matches)}"
        )
    return matches[0]


def build_disk_index(run_dir: Path, logger: logging.Logger, skip_json=True) -> dict[str, list[dict]]:
    logger.info(f"Indexing files under: {run_dir}")
    index: dict[str, list[dict]] = defaultdict(list)
    file_count = 0

    for p in run_dir.rglob("*"):
        if not p.is_file():
            continue

        if skip_json and p.name.lower().startswith("dfir-orc-") and p.suffix.lower() == ".json":
            continue

        entry = {
            "path": str(p),
            "size": p.stat().st_size,
            "relpath": str(p.relative_to(run_dir)),
            "name": p.name,
            "name_lower": p.name.lower(),
        }
        index[p.name.lower()].append(entry)
        file_count += 1

    logger.info(f"Indexed {file_count} files")
    return index


def build_outcome_inventory(
    outcome: dict,
    logger: logging.Logger,
) -> tuple[dict[str, list[dict]], dict[str, dict], dict[tuple[str, str], dict]]:
    file_index: dict[str, list[dict]] = defaultdict(list)
    archive_index: dict[str, dict] = {}
    command_index: dict[tuple[str, str], dict] = {}

    archive_count = 0
    command_count = 0
    file_count = 0

    for cs in outcome.get("command_set", []):
        archive_keyword = cs.get("name")
        archive_index[archive_keyword] = cs
        archive_count += 1

        for f in cs.get("archive", {}).get("files", []):
            file_index[f.get("name", "").lower()].append(
                {
                    "archive_keyword": archive_keyword,
                    "size": f.get("size"),
                    "name": f.get("name"),
                }
            )
            file_count += 1

        for cmd in cs.get("commands", []):
            command_index[(archive_keyword, cmd.get("name"))] = cmd
            command_count += 1

    logger.info(
        f"Built outcome inventory: {archive_count} archives, {command_count} commands, {file_count} archived files"
    )
    return file_index, archive_index, command_index


def emit_base_fields(outline: dict, outcome: dict, module_name: str) -> dict:
    return {
        "module": module_name,
        "orc_id": outcome.get("id") or outline.get("id"),
        "timestamp": outcome.get("timestamp") or outline.get("timestamp"),
        "computer_name": outcome.get("computer_name") or outline.get("computer_name"),
        "system_type": outcome.get("system_type") or outline.get("system_type"),
    }


def build_run_summary(outline: dict, outcome: dict, disk_index: dict[str, list[dict]]) -> dict:
    process_user = outline.get("process", {}).get("user", {})
    base = emit_base_fields(outline, outcome, "orc_outcome")

    expected_archive_count = len(outline.get("archives", []))
    outcome_archive_count = len(outcome.get("command_set", []))
    disk_file_count = sum(len(v) for v in disk_index.values())

    return {
        **base,
        "event_type": "orc_run_summary",
        "start": outcome.get("start") or outline.get("start"),
        "end": outcome.get("end"),
        "duration_seconds": duration_seconds(
            outcome.get("start") or outline.get("start"), outcome.get("end")
        ),
        "orc_version": outcome.get("wolf_launcher", {}).get("version") or outline.get("version"),
        "mothership_sha1": outcome.get("mothership", {}).get("sha1")
        or outline.get("mothership", {}).get("sha1"),
        "wolf_launcher_sha1": outcome.get("wolf_launcher", {}).get("sha1"),
        "mothership_command_line": outcome.get("mothership", {}).get("command_line")
        or outline.get("mothership", {}).get("command_line"),
        "wolf_launcher_command_line": outcome.get("wolf_launcher", {}).get("command_line")
        or outline.get("process", {}).get("command_line"),
        "output_path": outline.get("output"),
        "temp_path": outline.get("temp"),
        "user_name": process_user.get("username"),
        "user_sid": process_user.get("SID"),
        "user_elevated": process_user.get("elevated"),
        "user_locale": process_user.get("locale"),
        "user_language": process_user.get("language"),
        "expected_archive_count": expected_archive_count,
        "outcome_archive_count": outcome_archive_count,
        "disk_file_count": disk_file_count,
        "status": "ok",
        "status_code": 0,
    }


def validate_archives(
    outline: dict, outcome: dict, run_dir: Path, logger: logging.Logger
) -> tuple[list[dict], list[dict]]:
    base = emit_base_fields(outline, outcome, "orc_outcome")
    outcome_archives = {cs.get("name"): cs for cs in outcome.get("command_set", [])}
    events = []
    issues = []

    logger.info("Validating outer ORC archives")

    for archive in outline.get("archives", []):
        keyword = archive.get("keyword")
        expected_archive_name = archive.get("file")
        actual = outcome_archives.get(keyword)

        physical_path = run_dir / expected_archive_name if expected_archive_name else None
        physical_exists = physical_path.exists() if physical_path else False
        physical_size = physical_path.stat().st_size if physical_exists else None

        status = "ok"
        problem_list = []

        if not actual:
            status = "error"
            problem_list.append("missing_archive_group_in_outcome")

        if not physical_exists:
            status = "error"
            problem_list.append("missing_outer_archive_on_disk")
            logger.warning(f"Missing outer archive on disk: {expected_archive_name}")

        actual_archive_name = None
        actual_archive_size = None
        actual_archive_sha1 = None
        expected_command_count = len(archive.get("commands", []))
        actual_command_count = 0

        if actual:
            actual_archive_name = actual.get("archive", {}).get("name")
            actual_archive_size = actual.get("archive", {}).get("size")
            actual_archive_sha1 = actual.get("archive", {}).get("sha1")
            actual_command_count = len(actual.get("commands", []))

            if strip_p7b(actual_archive_name).lower() != (expected_archive_name or "").lower():
                status = "warning" if status == "ok" else status
                problem_list.append("archive_filename_mismatch")
                logger.warning(
                    f"Archive filename mismatch for {keyword}: expected={expected_archive_name}, outcome={actual_archive_name}"
                )

        events.append(
            {
                **base,
                "event_type": "orc_archive_validation",
                "archive_keyword": keyword,
                "expected_archive_name": expected_archive_name,
                "outcome_archive_name": actual_archive_name,
                "outcome_archive_size": actual_archive_size,
                "outcome_archive_sha1": actual_archive_sha1,
                "physical_archive_path": str(physical_path) if physical_path else None,
                "physical_archive_exists": physical_exists,
                "physical_archive_size": physical_size,
                "expected_command_count": expected_command_count,
                "actual_command_count": actual_command_count,
                "status": status,
                "status_code": status_code(status),
                "issues": problem_list,
            }
        )

        for p in problem_list:
            issues.append(
                {
                    **base,
                    "event_type": "orc_validation_issue",
                    "archive_keyword": keyword,
                    "severity": status,
                    "issue_code": p,
                    "status": status,
                    "status_code": status_code(status),
                }
            )

    return events, issues


def validate_commands(outline: dict, outcome: dict, logger: logging.Logger) -> tuple[list[dict], list[dict]]:
    base = emit_base_fields(outline, outcome, "orc_outcome")
    outcome_cmds = {}

    for cs in outcome.get("command_set", []):
        for cmd in cs.get("commands", []):
            outcome_cmds[(cs.get("name"), cmd.get("name"))] = cmd

    events = []
    issues = []

    logger.info("Validating commands")

    for archive in outline.get("archives", []):
        keyword = archive.get("keyword")

        for cmd in archive.get("commands", []):
            name = cmd.get("name")
            actual = outcome_cmds.get((keyword, name))

            if not actual:
                logger.warning(f"Missing command in outcome: archive={keyword}, command={name}")
                status = "error"
                problems = ["missing_command_in_outcome"]
                event = {
                    **base,
                    "event_type": "orc_command_validation",
                    "archive_keyword": keyword,
                    "command_name": name,
                    "tool": None,
                    "start": None,
                    "end": None,
                    "duration_seconds": None,
                    "exit_code": None,
                    "status": status,
                    "status_code": status_code(status),
                    "issues": problems,
                }
                events.append(event)

                for p in problems:
                    issues.append(
                        {
                            **base,
                            "event_type": "orc_validation_issue",
                            "archive_keyword": keyword,
                            "command_name": name,
                            "severity": status,
                            "issue_code": p,
                            "status": status,
                            "status_code": status_code(status),
                        }
                    )
                continue

            problems = []
            status = "ok"

            if actual.get("exit_code") != 0:
                status = "warning"
                problems.append("non_zero_exit_code")
                logger.warning(
                    f"Non-zero exit code for archive={keyword}, command={name}: {actual.get('exit_code')}"
                )

            dur = duration_seconds(actual.get("start"), actual.get("end"))
            if dur is not None and dur < 0:
                status = "warning"
                problems.append("negative_duration")
                logger.warning(f"Negative duration for archive={keyword}, command={name}")

            event = {
                **base,
                "event_type": "orc_command_validation",
                "archive_keyword": keyword,
                "command_name": name,
                "tool": actual.get("tool"),
                "start": actual.get("start"),
                "end": actual.get("end"),
                "duration_seconds": dur,
                "exit_code": actual.get("exit_code"),
                "pid": actual.get("pid"),
                "sha1": actual.get("sha1"),
                "status": status,
                "status_code": status_code(status),
                "issues": problems,
            }
            events.append(event)

            for p in problems:
                issues.append(
                    {
                        **base,
                        "event_type": "orc_validation_issue",
                        "archive_keyword": keyword,
                        "command_name": name,
                        "severity": status,
                        "issue_code": p,
                        "status": status,
                        "status_code": status_code(status),
                    }
                )

    return events, issues


def emit_outline_system_events(outline: dict, outcome: dict, logger: logging.Logger) -> list[dict]:
    base = emit_base_fields(outline, outcome, "orc_outcome")
    events = []

    system = outline.get("system", {})
    if not system:
        logger.info("No outline.system block found")
        return events

    logger.info("Emitting system inventory from outline.system")
    os_info = system.get("operating_system", {})
    mem = system.get("physical_memory", {})
    tz = os_info.get("time_zone", {})

    events.append(
        {
            **base,
            "event_type": "orc_system_summary",
            "system_name": system.get("name"),
            "system_fullname": system.get("fullname"),
            "system_role_type": system.get("type"),
            "codepage": system.get("codepage"),
            "codepage_name": system.get("codepage_name"),
            "hypervisor": system.get("hypervisor"),
            "architecture": system.get("architecture"),
            "os_description": os_info.get("description"),
            "os_version": os_info.get("version"),
            "os_locale": os_info.get("locale"),
            "os_language": os_info.get("language"),
            "os_install_date": os_info.get("install_date"),
            "os_install_time": os_info.get("install_time"),
            "os_shutdown_time": os_info.get("shutdown_time"),
            "os_tags": os_info.get("tag", []),
            "timezone_daylight": tz.get("daylight"),
            "timezone_standard": tz.get("standard"),
            "timezone_current": tz.get("current"),
            "timezone_current_bias": tz.get("current_bias"),
            "memory_current_load": mem.get("current_load"),
            "memory_physical": mem.get("physical"),
            "memory_pagefile": mem.get("pagefile"),
            "memory_available_physical": mem.get("available_physical"),
            "memory_available_pagefile": mem.get("available_pagefile"),
            "status": "ok",
            "status_code": 0,
        }
    )

    for cpu in system.get("cpu", []):
        events.append(
            {
                **base,
                "event_type": "orc_system_cpu",
                "manufacturer": cpu.get("manufacturer"),
                "name": cpu.get("name"),
                "physical_processors": cpu.get("physical_processors"),
                "logical_processors": cpu.get("logical_processors"),
                "hyperthreading": cpu.get("hyperthreading"),
                "status": "ok",
                "status_code": 0,
            }
        )

    for drive in system.get("physical_drives", []):
        events.append(
            {
                **base,
                "event_type": "orc_system_drive",
                "path": drive.get("path"),
                "type": drive.get("type"),
                "serial": drive.get("serial"),
                "size": drive.get("size"),
                "drive_status": drive.get("status"),
                "status": "ok",
                "status_code": 0,
            }
        )

    for vol in system.get("mounted_volumes", []):
        events.append(
            {
                **base,
                "event_type": "orc_system_volume",
                "path": vol.get("path"),
                "label": vol.get("label"),
                "serial": vol.get("serial"),
                "file_system": vol.get("file_system"),
                "device_id": vol.get("device_id"),
                "is_boot": vol.get("is_boot"),
                "is_system": vol.get("is_system"),
                "size": vol.get("size"),
                "freespace": vol.get("freespace"),
                "volume_type": vol.get("type"),
                "status": "ok",
                "status_code": 0,
            }
        )

    network = system.get("network", {})
    for adapter in network.get("adapter", []):
        events.append(
            {
                **base,
                "event_type": "orc_system_network_adapter",
                "adapter_name": adapter.get("name"),
                "friendly_name": adapter.get("friendly_name"),
                "description": adapter.get("description"),
                "physical": adapter.get("physical"),
                "dns_suffix": adapter.get("dns_suffix"),
                "dns_server": adapter.get("dns_server", []),
                "addresses": adapter.get("address", []),
                "status": "ok",
                "status_code": 0,
            }
        )

    for qfe in os_info.get("qfe", []):
        events.append(
            {
                **base,
                "event_type": "orc_system_hotfix",
                "hotfix_id": qfe.get("hotfix_id"),
                "installed_on": qfe.get("installed_on"),
                "status": "ok",
                "status_code": 0,
            }
        )

    profile_list = outline.get("profile_list", {})
    events.append(
        {
            **base,
            "event_type": "orc_profile_summary",
            "default_profile": profile_list.get("default_profile"),
            "profiles_directory": profile_list.get("profiles_directory"),
            "program_data": profile_list.get("program_data"),
            "public_path": profile_list.get("public_path"),
            "status": "ok",
            "status_code": 0,
        }
    )

    for profile in profile_list.get("profile", []):
        events.append(
            {
                **base,
                "event_type": "orc_profile",
                "sid": profile.get("sid"),
                "path": profile.get("path"),
                "user": profile.get("user"),
                "local_load_time": profile.get("local_load_time"),
                "local_unload_time": profile.get("local_unload_time"),
                "key_last_write": profile.get("key_last_write"),
                "status": "ok",
                "status_code": 0,
            }
        )

    return events


def xml_local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def find_xml_candidates_from_outcome(outcome: dict, logger: logging.Logger) -> list[dict]:
    candidates = []

    for cs in outcome.get("command_set", []):
        archive_keyword = cs.get("name")
        for f in cs.get("archive", {}).get("files", []):
            name = f.get("name", "")
            lname = name.lower()
            if lname == "config.xml" or lname.endswith("_cli_config.xml"):
                candidates.append(
                    {
                        "archive_keyword": archive_keyword,
                        "xml_name": name,
                        "xml_name_lower": lname,
                        "size_outcome": f.get("size"),
                    }
                )

    logger.info(f"Found {len(candidates)} XML candidates from outcome inventory")
    return candidates


def resolve_xml_path(
    extracted_root: Path,
    archive_keyword: str,
    xml_name: str,
    logger: logging.Logger,
) -> Path | None:
    if not extracted_root.exists():
        return None

    keyword_lower = (archive_keyword or "").lower()
    archive_dir = None

    for child in extracted_root.iterdir():
        if child.is_dir() and child.name.lower() == keyword_lower:
            archive_dir = child
            break

    search_roots = []
    if archive_dir:
        search_roots.append(archive_dir)
    search_roots.append(extracted_root)

    xml_name_lower = xml_name.lower()

    for root in search_roots:
        for p in root.rglob("*"):
            if p.is_file() and p.name.lower() == xml_name_lower:
                logger.debug(f"Resolved XML {xml_name} to {p}")
                return p

    logger.warning(f"Could not resolve XML on disk: archive={archive_keyword}, xml={xml_name}")
    return None


def parse_config_xml_limits(root: ET.Element) -> dict:
    limits = {
        "limit_timeout_seconds": None,
        "limit_max_file_count": None,
        "limit_max_file_size_bytes": None,
        "limit_max_total_size_bytes": None,
    }

    for elem in root.iter():
        name = xml_local_name(elem.tag)

        if name == "restrictions":
            elapsed = elem.attrib.get("ElapsedTimeLimit")
            if elapsed is not None:
                try:
                    limits["limit_timeout_seconds"] = int(elapsed)
                except ValueError:
                    pass

        if name == "samples":
            max_per_sample = elem.attrib.get("MaxPerSampleBytes")
            max_total = elem.attrib.get("MaxTotalBytes")
            max_count = elem.attrib.get("MaxSampleCount")

            parsed = parse_size_to_bytes(max_per_sample)
            if parsed is not None:
                limits["limit_max_file_size_bytes"] = parsed

            parsed = parse_size_to_bytes(max_total)
            if parsed is not None:
                limits["limit_max_total_size_bytes"] = parsed

            if max_count and str(max_count).upper() != "N/A":
                try:
                    limits["limit_max_file_count"] = int(max_count)
                except ValueError:
                    pass

    return limits


def parse_command_outputs_from_config(root: ET.Element) -> dict[tuple[str, str], list[dict]]:
    result = defaultdict(list)

    for archive in root.findall(".//archive"):
        archive_keyword = archive.attrib.get("keyword")
        if not archive_keyword:
            continue

        for command in archive.findall("./command"):
            command_keyword = command.attrib.get("keyword")
            if not command_keyword:
                continue

            for output in command.findall("./output"):
                name = output.attrib.get("name")
                source = output.attrib.get("source")
                if not name:
                    continue

                result[(archive_keyword.lower(), command_keyword.lower())].append(
                    {
                        "name_raw": name,
                        "source": source,
                    }
                )

    return result


def map_outline_command_to_config_keyword(outline: dict) -> dict[tuple[str, str], str]:
    mapping = {}
    for archive in outline.get("archives", []):
        archive_keyword = (archive.get("keyword") or "").lower()
        for cmd in archive.get("commands", []):
            outline_name = (cmd.get("name") or "").lower()
            config_keyword = (cmd.get("keyword") or cmd.get("name") or "").lower()
            if archive_keyword and outline_name and config_keyword:
                mapping[(archive_keyword, outline_name)] = config_keyword
    return mapping


def parse_command_log_observations(log_path: Path, logger: logging.Logger) -> dict:
    observations = {
        "no_limits": None,
        "observed_file_count": None,
        "observed_max_file_size_bytes": None,
        "observed_total_size_bytes": None,
        "observed_duration_seconds": None,
        "log_start": None,
        "log_finish": None,
        "matched_files": [],
    }

    size_values = []
    matched_count = 0

    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        logger.exception(f"Unable to read log file: {log_path}")
        return observations

    m = re.search(r"^\s*NoLimits:\s*(True|False)\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    if m:
        observations["no_limits"] = m.group(1).lower() == "true"

    m = re.search(r"^\s*Start time:\s*([0-9T:\-\.Z]+)\s*$", text, flags=re.MULTILINE)
    if m:
        observations["log_start"] = m.group(1)

    m = re.search(r"^\s*Finish time:\s*([0-9T:\-\.Z]+)\s*$", text, flags=re.MULTILINE)
    if m:
        observations["log_finish"] = m.group(1)

    if observations["log_start"] and observations["log_finish"]:
        observations["observed_duration_seconds"] = duration_seconds(
            observations["log_start"], observations["log_finish"]
        )

    for m in re.finditer(r"^(.+?) matched \(([0-9]+) bytes\)\s*$", text, flags=re.MULTILINE):
        path_text = m.group(1).strip()
        size_val = int(m.group(2))
        matched_count += 1
        size_values.append(size_val)
        observations["matched_files"].append(
            {
                "path": path_text,
                "size_bytes": size_val,
            }
        )

    if matched_count > 0:
        observations["observed_file_count"] = matched_count
        observations["observed_max_file_size_bytes"] = max(size_values)
        observations["observed_total_size_bytes"] = sum(size_values)

    items_lines = re.findall(
        r"items:\s*([0-9]+)/([0-9]+)",
        text,
        flags=re.IGNORECASE,
    )
    if observations["observed_file_count"] is None and items_lines:
        try:
            observations["observed_file_count"] = max(int(x[0]) for x in items_lines)
        except Exception:
            pass

    return observations


def is_config_file_name(name: str) -> bool:
    lname = (name or "").lower()
    return lname == "config.xml" or lname.endswith("_cli_config.xml")


def output_role(name: str, source: str | None) -> str:
    """
    Classify an output from Config.xml.

    collected:
      - File
      - StdOut
      - StdOutErr when materialized into a real artifact file (.txt/.csv/.xml/.json/.out/.7z)

    support:
      - StdErr
      - *.err
      - *.getthis
      - config xml
      - *.log when produced from StdErr/StdOutErr

    unknown:
      - anything else
    """
    lname = (name or "").lower()
    src = (source or "").strip().lower()

    if is_config_file_name(lname):
        return "support"
    if lname.endswith(".err") or lname.endswith(".getthis"):
        return "support"

    if src == "file":
        return "collected"
    if src == "stdout":
        return "collected"
    if src == "stderr":
        return "support"

    if src == "stdouterr":
        if lname.endswith(".log"):
            return "support"
        if any(
            lname.endswith(ext)
            for ext in (".txt", ".csv", ".xml", ".json", ".out", ".7z")
        ):
            return "collected"
        return "support"

    return "unknown"


def is_container_output_name(name: str) -> bool:
    return (name or "").lower().endswith(".7z")


def list_files_recursive(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def resolve_extracted_artifact_path(
    extracted_root: Path,
    archive_keyword: str,
    output_name_raw: str,
    computer_name: str,
    logger: logging.Logger,
    outer_archive_name: str | None = None,
) -> Path | None:
    """
    Map a collected output from config/outcome to the extracted artifact path on disk.

    Examples:
      event_{FullComputerName}.7z -> extracted_files/logs/event_vagrant-10/
      samhive_{FullComputerName}.7z -> extracted_files/sam/samhive_vagrant-10/
      autoruns_{FullComputerName}.csv -> extracted_files/external/autoruns_vagrant-10.csv
    """
    archive_dir = extracted_root / archive_keyword.lower()

    if not archive_dir.exists() and outer_archive_name:
        archive_tail = Path(outer_archive_name).stem.split("_")[-1]
        archive_dir = extracted_root / archive_tail

    if not archive_dir.exists():
        logger.warning(f"Archive extracted dir not found: {archive_dir}")
        return None

    expected_name = normalize_filename(output_name_raw, computer_name)
    expected_stem = Path(expected_name).stem.lower()

    # 1) Exact file match
    for p in archive_dir.rglob("*"):
        if p.is_file() and p.name.lower() == expected_name:
            return p

    # 2) Exact directory match for extracted container content
    for p in archive_dir.rglob("*"):
        if p.is_dir() and p.name.lower() == expected_stem:
            return p

    # 3) Exact file stem match
    for p in archive_dir.rglob("*"):
        if p.is_file() and p.stem.lower() == expected_stem:
            return p

    # 4) Prefix fallback
    prefix_matches = []
    for p in archive_dir.rglob("*"):
        name_l = p.name.lower()
        stem_l = p.stem.lower()
        if name_l.startswith(expected_stem) or stem_l.startswith(expected_stem):
            prefix_matches.append(p)

    if is_container_output_name(output_name_raw):
        dir_matches = [p for p in prefix_matches if p.is_dir()]
        if dir_matches:
            dir_matches.sort(key=lambda x: (len(str(x.parts)), str(x)))
            return dir_matches[0]

    if prefix_matches:
        prefix_matches.sort(key=lambda x: (0 if x.is_file() else 1, len(str(x.parts)), str(x)))
        return prefix_matches[0]

    logger.warning(
        f"Could not resolve extracted artifact path: archive={archive_keyword}, output={output_name_raw}"
    )
    return None


def collect_main_output_disk_metrics(
    extracted_root: Path,
    archive_keyword: str,
    output_name_raw: str,
    computer_name: str,
    logger: logging.Logger,
    outer_archive_name: str | None = None,
) -> dict:
    resolved = resolve_extracted_artifact_path(
        extracted_root=extracted_root,
        archive_keyword=archive_keyword,
        output_name_raw=output_name_raw,
        computer_name=computer_name,
        logger=logger,
        outer_archive_name=outer_archive_name,
    )

    result = {
        "resolved_disk_path": str(resolved) if resolved else None,
        "present_on_disk": resolved is not None,
        "disk_collected_file_count": None,
        "disk_collected_total_size": None,
        "disk_collected_max_file_size": None,
    }

    if not resolved:
        return result

    if resolved.is_file():
        size = resolved.stat().st_size
        result["disk_collected_file_count"] = 1
        result["disk_collected_total_size"] = size
        result["disk_collected_max_file_size"] = size
        return result

    files = list_files_recursive(resolved)
    if not files:
        result["disk_collected_file_count"] = 0
        result["disk_collected_total_size"] = 0
        result["disk_collected_max_file_size"] = 0
        return result

    sizes = [f.stat().st_size for f in files]
    result["disk_collected_file_count"] = len(files)
    result["disk_collected_total_size"] = sum(sizes)
    result["disk_collected_max_file_size"] = max(sizes)
    return result


def evaluate_limits(
    limit_timeout_seconds,
    limit_max_file_count,
    limit_max_file_size_bytes,
    limit_max_total_size_bytes,
    observed_duration_seconds,
    observed_file_count,
    observed_max_file_size_bytes,
    observed_total_size_bytes,
):
    triggered_limits = []
    reasons = []

    if limit_timeout_seconds is not None:
        if observed_duration_seconds is None:
            reasons.append("missing observed duration for timeout evaluation")
        elif observed_duration_seconds >= limit_timeout_seconds:
            triggered_limits.append("timeout")

    if limit_max_file_count is not None:
        if observed_file_count is None:
            reasons.append("missing observed file count for max file count evaluation")
        elif observed_file_count >= limit_max_file_count:
            triggered_limits.append("max_file_count")

    if limit_max_file_size_bytes is not None:
        if observed_max_file_size_bytes is None:
            reasons.append("missing observed file sizes for max file size evaluation")
        elif observed_max_file_size_bytes >= limit_max_file_size_bytes:
            triggered_limits.append("max_file_size")

    if limit_max_total_size_bytes is not None:
        if observed_total_size_bytes is None:
            reasons.append("missing observed total size for max total size evaluation")
        elif observed_total_size_bytes >= limit_max_total_size_bytes:
            triggered_limits.append("max_total_size")

    return triggered_limits, reasons


def reason_join(parts: list[str]) -> str | None:
    parts = [p for p in parts if p]
    if not parts:
        return None
    return "; ".join(parts)


def parse_orc_artifact_evaluations(
    outline: dict,
    outcome: dict,
    run_dir: Path,
    disk_index: dict[str, list[dict]],
    logger: logging.Logger,
) -> tuple[list[dict], list[dict]]:
    base = emit_base_fields(outline, outcome, "orc_outcome")
    events = []
    issues = []

    logger.info("Building ORC collected artifact evaluation events")

    extracted_root = run_dir / "extracted_files"
    candidates = find_xml_candidates_from_outcome(outcome, logger)
    outcome_file_index, _, command_index = build_outcome_inventory(outcome, logger)
    command_name_to_config_keyword = map_outline_command_to_config_keyword(outline)

    config_limits_by_archive_command = {}
    config_outputs_by_archive_command = defaultdict(list)
    cli_limits_by_archive = {}
    cli_limits_by_archive_command = {}

    # Parse XML files referenced by outcome
    for candidate in candidates:
        archive_keyword = candidate["archive_keyword"]
        xml_name = candidate["xml_name"]
        xml_path = resolve_xml_path(extracted_root, archive_keyword, xml_name, logger)

        if not xml_path:
            issues.append(
                {
                    **base,
                    "event_type": "orc_validation_issue",
                    "archive_keyword": archive_keyword,
                    "expected_file_name": xml_name,
                    "severity": "warning",
                    "issue_code": "xml_file_missing_on_disk",
                    "status": "warning",
                    "status_code": 1,
                }
            )
            continue

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception as exc:
            logger.exception(f"Failed to parse XML: {xml_path}")
            issues.append(
                {
                    **base,
                    "event_type": "orc_validation_issue",
                    "archive_keyword": archive_keyword,
                    "expected_file_name": xml_name,
                    "severity": "error",
                    "issue_code": "xml_parse_error",
                    "xml_error": str(exc),
                    "status": "error",
                    "status_code": 2,
                }
            )
            continue

        lname = xml_name.lower()

        # Use the first global Config.xml as authoritative source for outputs and archive restrictions
        if lname == "config.xml":
            if config_outputs_by_archive_command:
                continue

            outputs_map = parse_command_outputs_from_config(root)
            for key, value in outputs_map.items():
                config_outputs_by_archive_command[key].extend(value)

            for archive in root.findall(".//archive"):
                archive_kw = (archive.attrib.get("keyword") or "").lower()
                limits = parse_config_xml_limits(archive)

                for command in archive.findall("./command"):
                    cmd_kw = (command.attrib.get("keyword") or "").lower()
                    if archive_kw and cmd_kw:
                        config_limits_by_archive_command[(archive_kw, cmd_kw)] = limits.copy()

        elif lname.endswith("_cli_config.xml"):
            limits = parse_config_xml_limits(root)
            cli_limits_by_archive.setdefault(archive_keyword.lower(), []).append(
                {
                    "xml_name": xml_name,
                    "xml_path": str(xml_path),
                    "limits": limits,
                }
            )

    computer_name = outcome.get("computer_name") or outline.get("computer_name") or ""

    # Associate CLI XMLs to outline commands by matching declared output names
    for archive in outline.get("archives", []):
        archive_keyword = archive.get("keyword")
        archive_kw_lower = (archive_keyword or "").lower()

        for cmd in archive.get("commands", []):
            outline_command_name = cmd.get("name")
            outline_command_name_lower = (outline_command_name or "").lower()

            for out in cmd.get("output", []):
                out_name_raw = out.get("name", "")
                normalized_expected = normalize_filename(out_name_raw, computer_name)

                for cli_entry in cli_limits_by_archive.get(archive_kw_lower, []):
                    xml_name = cli_entry["xml_name"]
                    xml_lname = xml_name.lower()

                    if normalized_expected and normalized_expected in xml_lname:
                        cli_limits_by_archive_command[(archive_kw_lower, outline_command_name_lower)] = {
                            "xml_name": xml_name,
                            "xml_path": cli_entry["xml_path"],
                            **cli_entry["limits"],
                        }

    for archive in outline.get("archives", []):
        archive_keyword = archive.get("keyword")
        archive_kw_lower = (archive_keyword or "").lower()

        outer_archive_name = archive.get("file")
        outer_archive_present_on_disk = None
        outer_archive_size_disk = None
        outer_archive_size_outcome = None

        if outer_archive_name:
            outer_archive_path = run_dir / outer_archive_name
            outer_archive_present_on_disk = outer_archive_path.exists()
            outer_archive_size_disk = outer_archive_path.stat().st_size if outer_archive_present_on_disk else None

        for cs in outcome.get("command_set", []):
            if cs.get("name") == archive_keyword:
                outer_archive_size_outcome = cs.get("archive", {}).get("size")
                break

        for cmd in archive.get("commands", []):
            command_name = cmd.get("name")
            command_name_lower = (command_name or "").lower()

            config_command_keyword_lower = command_name_to_config_keyword.get(
                (archive_kw_lower, command_name_lower),
                command_name_lower,
            )

            # Prefer outputs declared in Config.xml, fallback to outline outputs
            command_outputs = config_outputs_by_archive_command.get(
                (archive_kw_lower, config_command_keyword_lower),
                [],
            )
            if not command_outputs:
                command_outputs = [
                    {
                        "name_raw": out.get("name", ""),
                        "source": out.get("source"),
                    }
                    for out in cmd.get("output", [])
                ]

            # Use Config.xml source + output name to determine collected artifacts.
            collected_outputs = [
                {
                    "name_raw": out.get("name_raw"),
                    "source": out.get("source"),
                }
                for out in command_outputs
                if output_role(out.get("name_raw", ""), out.get("source")) == "collected"
            ]

            support_outputs = [
                {
                    "name_raw": out.get("name_raw"),
                    "source": out.get("source"),
                }
                for out in command_outputs
                if output_role(out.get("name_raw", ""), out.get("source")) == "support"
            ]

            main_output = collected_outputs[0] if collected_outputs else None

            collected_name_raw = main_output["name_raw"] if main_output else None
            collected_name_expected = (
                normalize_filename(collected_name_raw, computer_name) if collected_name_raw else None
            )

            collected_present_in_outcome = False
            collected_size_outcome = None
            if collected_name_expected:
                outcome_hits = outcome_file_index.get(collected_name_expected, [])
                if outcome_hits:
                    collected_present_in_outcome = True
                    collected_size_outcome = outcome_hits[0].get("size")

            config_limits = config_limits_by_archive_command.get(
                (archive_kw_lower, config_command_keyword_lower),
                {}
            )
            cli_limits = cli_limits_by_archive_command.get((archive_kw_lower, command_name_lower), {})

            limit_timeout_seconds = cli_limits.get("limit_timeout_seconds")
            if limit_timeout_seconds is None:
                limit_timeout_seconds = config_limits.get("limit_timeout_seconds")

            limit_max_file_count = cli_limits.get("limit_max_file_count")
            if limit_max_file_count is None:
                limit_max_file_count = config_limits.get("limit_max_file_count")

            limit_max_file_size_bytes = cli_limits.get("limit_max_file_size_bytes")
            if limit_max_file_size_bytes is None:
                limit_max_file_size_bytes = config_limits.get("limit_max_file_size_bytes")

            limit_max_total_size_bytes = cli_limits.get("limit_max_total_size_bytes")
            if limit_max_total_size_bytes is None:
                limit_max_total_size_bytes = config_limits.get("limit_max_total_size_bytes")

            config_source = cli_limits.get("xml_name")
            if not config_source and config_limits:
                config_source = "Config.xml"

            outcome_cmd = command_index.get((archive_keyword, command_name))
            observed_duration_seconds = None
            if outcome_cmd:
                observed_duration_seconds = duration_seconds(
                    outcome_cmd.get("start"),
                    outcome_cmd.get("end"),
                )

            log_source = None
            log_observations = None

            # Find one support log for extra observations
            possible_logs = []
            for out in support_outputs:
                expected_name = normalize_filename(out.get("name_raw", ""), computer_name)
                possible_logs.append(expected_name)

            for log_name in possible_logs:
                hits_log = disk_index.get(log_name, [])
                if hits_log:
                    log_path = Path(hits_log[0]["path"])
                    log_source = log_path.name
                    log_observations = parse_command_log_observations(log_path, logger)
                    break

            if observed_duration_seconds is None and log_observations and log_observations.get("observed_duration_seconds") is not None:
                observed_duration_seconds = log_observations["observed_duration_seconds"]

            no_limits = log_observations.get("no_limits") if log_observations else None

            disk_metrics = {
                "resolved_disk_path": None,
                "present_on_disk": False,
                "disk_collected_file_count": None,
                "disk_collected_total_size": None,
                "disk_collected_max_file_size": None,
            }
            if collected_name_raw:
                disk_metrics = collect_main_output_disk_metrics(
                    extracted_root=extracted_root,
                    archive_keyword=archive_keyword,
                    output_name_raw=collected_name_raw,
                    computer_name=computer_name,
                    logger=logger,
                    outer_archive_name=outer_archive_name,
                )

            observed_file_count = disk_metrics["disk_collected_file_count"]
            observed_total_size_bytes = disk_metrics["disk_collected_total_size"]
            observed_max_file_size_bytes = disk_metrics["disk_collected_max_file_size"]

            # Fallback to log-derived observations only if main disk metrics are absent
            if observed_file_count is None and log_observations and log_observations.get("observed_file_count") is not None:
                observed_file_count = log_observations["observed_file_count"]

            if observed_max_file_size_bytes is None and log_observations and log_observations.get("observed_max_file_size_bytes") is not None:
                observed_max_file_size_bytes = log_observations["observed_max_file_size_bytes"]

            if observed_total_size_bytes is None and log_observations and log_observations.get("observed_total_size_bytes") is not None:
                observed_total_size_bytes = log_observations["observed_total_size_bytes"]

            triggered_limits, eval_reasons = evaluate_limits(
                limit_timeout_seconds=limit_timeout_seconds,
                limit_max_file_count=limit_max_file_count,
                limit_max_file_size_bytes=limit_max_file_size_bytes,
                limit_max_total_size_bytes=limit_max_total_size_bytes,
                observed_duration_seconds=observed_duration_seconds,
                observed_file_count=observed_file_count,
                observed_max_file_size_bytes=observed_max_file_size_bytes,
                observed_total_size_bytes=observed_total_size_bytes,
            )

            reason_parts = []

            if triggered_limits:
                status = "error"
                reason_parts.append("configured limit reached")
            elif collected_name_raw and not collected_present_in_outcome:
                status = "warning"
                reason_parts.append("collected artifact missing in outcome")
            elif collected_name_raw and not disk_metrics["present_on_disk"]:
                status = "warning"
                reason_parts.append("collected artifact missing on disk")
            elif eval_reasons and any(
                v is not None for v in [
                    limit_timeout_seconds,
                    limit_max_file_count,
                    limit_max_file_size_bytes,
                    limit_max_total_size_bytes,
                ]
            ):
                status = "warning"
                reason_parts.extend(eval_reasons)
            elif no_limits is True:
                status = "ok"
                reason_parts.append("no limits enabled")
            else:
                status = "ok"

            events.append(
                {
                    **base,
                    "event_type": "orc_artifact_evaluation",
                    "archive_keyword": archive_keyword,
                    "command_name": command_name,
                    "outer_archive_name": outer_archive_name,
                    "outer_archive_present_on_disk": outer_archive_present_on_disk,
                    "outer_archive_size_disk": outer_archive_size_disk,
                    "outer_archive_size_outcome": outer_archive_size_outcome,
                    "config_source": config_source,
                    "log_source": log_source,
                    "collected_name_raw": collected_name_raw,
                    "collected_name_expected": collected_name_expected,
                    "collected_present_in_outcome": collected_present_in_outcome,
                    "collected_size_outcome": collected_size_outcome,
                    "collected_resolved_disk_path": disk_metrics["resolved_disk_path"],
                    "collected_present_on_disk": disk_metrics["present_on_disk"],
                    "observed_duration_seconds": observed_duration_seconds,
                    "disk_collected_file_count": observed_file_count,
                    "disk_collected_total_size": observed_total_size_bytes,
                    "disk_collected_max_file_size": observed_max_file_size_bytes,
                    "limit_timeout_seconds": limit_timeout_seconds,
                    "limit_max_file_count": limit_max_file_count,
                    "limit_max_file_size_bytes": limit_max_file_size_bytes,
                    "limit_max_total_size_bytes": limit_max_total_size_bytes,
                    "triggered_limits": triggered_limits,
                    "status": status,
                    "status_code": status_code(status),
                    "reason": reason_join(reason_parts),
                }
            )

    logger.info(f"Built {len(events)} collected artifact evaluation events")
    return events, issues


def write_jsonl(path: Path, records: list[dict], logger: logging.Logger) -> None:
    logger.info(f"Writing {len(records)} records to {path}")
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logger = setup_logger(args.verbose)

    try:
        run_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting orc_outcome on: {run_dir}")

        outcome_path = find_single_json(run_dir, "outcome", logger)
        outline_path = find_single_json(run_dir, "outline", logger)

        outcome_data = load_json(outcome_path, logger)
        outline_data = load_json(outline_path, logger)

        outcome = get_outcome(outcome_data)
        outline = get_outline(outline_data)

        disk_index = build_disk_index(run_dir, logger)
        records = []

        records.append(build_run_summary(outline, outcome, disk_index))

        archive_events, archive_issues = validate_archives(outline, outcome, run_dir, logger)
        command_events, command_issues = validate_commands(outline, outcome, logger)
        system_events = emit_outline_system_events(outline, outcome, logger)
        artifact_events, artifact_issues = parse_orc_artifact_evaluations(
            outline=outline,
            outcome=outcome,
            run_dir=run_dir,
            disk_index=disk_index,
            logger=logger,
        )

        records.extend(archive_events)
        records.extend(command_events)
        records.extend(system_events)
        records.extend(artifact_events)
        records.extend(archive_issues)
        records.extend(command_issues)
        records.extend(artifact_issues)

        computer_name = outcome.get("computer_name") or outline.get("computer_name") or run_dir.name
        ts = outcome.get("timestamp") or outline.get("timestamp") or "unknown"
        out_file = output_dir / f"orc_outcome_{computer_name}_{ts}.jsonl"
        write_jsonl(out_file, records, logger)

        logger.info("orc_outcome completed successfully")

    except Exception:
        logger.exception("orc_outcome failed")
        raise


if __name__ == "__main__":
    main()