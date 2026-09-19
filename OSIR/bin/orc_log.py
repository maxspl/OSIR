#!/usr/bin/env python3
"""Parse the DFIR ORC execution log (DFIR-ORC_<type>_<host>_<date>_<time>.log) into JSON Lines.

The log is the one record of the collection that always travels with it - even when the archives
were extracted before OSIR saw them and no Outcome file came along. It says what DFIR ORC was asked
to collect and what it actually did:

  orc_run      the run itself: version, computer, OS, account (elevated or not), run id, output
               and temp directories, the archives (command sets) it was configured for, the keys
               enabled, limits, the DFIR-Orc.exe hash, and whether the log reaches the end of the run;
  orc_command  one line per command (GetEVT, NTFSInfo, GetRam...): its archive, start, end, duration,
               pid and outcome - success, error with its exit code, or still running when the log
               stops (the log was copied before DFIR ORC finished);
  orc_archive  one line per archive (command set): started, completed, size, how long its commands took;
  orc_message  the warnings and errors DFIR ORC logged ([W] / [E] / [C] lines).

    orc_log.py --input-dir <extract_orc/Endpoint_X> --output-dir <case>/orc_log

The output file is orc_log_<host>_<date>_<time>.jsonl; <host> is the Endpoint directory's name, the
same host OSIR indexes the rest of the machine under.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LINE = re.compile(r"^(?P<ts>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z) \[(?P<lvl>\w)\] ?(?P<msg>.*)$")
# "<ts>   <keyword>   <command>   <status>" - the scheduler's own summary lines
STATUS = re.compile(r"^(?P<ts>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s{2,}(?P<keyword>\S+)\s{2,}(?P<command>\S+)\s{2,}(?P<status>.+)$")
PARAM = re.compile(r"^\s{4}(?P<name>[A-Za-z][\w /-]*?):\s+(?P<value>.*)$")
LEVELS = {"D": "debug", "I": "info", "W": "warning", "E": "error", "C": "critical"}


def iso(ts):
    """'2026-01-02T17:45:22.848Z' -> '2026-01-02T17:45:22Z' (the format the Splunk block parses)."""
    return ts[:19] + "Z" if ts else None


def seconds(a, b):
    if not a or not b:
        return None
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return int((datetime.strptime(iso(b), fmt) - datetime.strptime(iso(a), fmt)).total_seconds())


def parse(path, extracted_dir=None):
    run = {"event_type": "orc_run", "expected_archives": [], "enable_keys": [], "disable_keys": []}
    commands, archives, messages = {}, {}, []
    in_params, list_param = False, None
    first_ts = last_ts = None
    job_complete = 0

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(raw)
        if not m:
            continue
        ts, lvl, msg = m.group("ts"), m.group("lvl"), m.group("msg")
        first_ts = first_ts or ts
        last_ts = ts

        if msg.startswith("WolfLauncher v"):
            run["orc_version"] = msg.split(" ", 1)[1].strip()
        am = re.match(r"Archive file name specified is '(?P<name>[^']+)'", msg)
        if am:
            key = re.sub(r"\.7z$", "", am.group("name")).rsplit("_", 1)[-1]
            run["expected_archives"].append(key)
            continue
        hm = re.match(r"Hash for '(?P<file>[^']+)': SHA1:(?P<sha1>[0-9A-Fa-f]{40})", msg)
        if hm and hm.group("file").lower().endswith("dfir-orc.exe"):
            run["orc_exe_path"], run["orc_exe_sha1"] = hm.group("file"), hm.group("sha1").lower()

        # the Parameters block: "    Name:   value", list values on the following indented lines
        if msg.strip() == "Parameters" and "start_time" not in run:
            in_params = True
            continue
        if in_params:
            pm = PARAM.match(msg)
            if pm:
                name = pm.group("name").strip().lower().replace(" ", "_").replace("-", "_")
                value = pm.group("value").strip()
                if name in ("enable_keys", "disable_keys"):
                    list_param = name
                    if value and value != "None":
                        run[name].append(value)
                else:
                    list_param = None
                    run[name] = value
                continue
            if list_param and msg.strip() and msg.startswith(" " * 10):
                run[list_param].append(msg.strip())
                continue
            if not msg.strip():
                in_params = False if "start_time" in run else in_params
                list_param = None
                continue

        sm = STATUS.match(msg)
        if sm and lvl == "I":
            kw, cmd, status = sm.group("keyword"), sm.group("command"), sm.group("status").strip()
            when = sm.group("ts")
            if cmd == "Archive":
                a = archives.setdefault(kw, {"event_type": "orc_archive", "archive": kw, "status": "started"})
                if status.startswith("Started"):
                    a["start"] = when
                elif status.startswith("Ended"):
                    em = re.search(r"output: (\d+) bytes", status)
                    a["bytes"] = int(em.group(1)) if em else None
                    a["end"] = when
                    a["status"] = "archived"
                elif status.startswith("Completed:"):
                    cm = re.match(r"Completed: (?P<path>.+?)(?: \((?P<size>[^)]+)\))?$", status)
                    a["archive_path"] = cm.group("path") if cm else status
                    a["size"] = cm.group("size") if cm else None
                    a["end"] = a.get("end") or when
                    a["status"] = "completed"
                elif status.startswith("Add file:"):
                    a["files_added"] = a.get("files_added", 0) + 1
                continue
            if kw == "WolfLauncher":
                continue
            key = (kw, cmd)
            c = commands.setdefault(key, {"event_type": "orc_command", "archive": kw, "command": cmd,
                                          "status": "started"})
            pid = re.search(r"pid: (\d+)", status)
            if pid:
                c["pid"] = int(pid.group(1))
            if status.startswith("Started"):
                c["start"] = when
            elif status.startswith("Successfully terminated"):
                c["end"], c["status"] = when, "success"
            elif "error" in status.lower() or status.startswith("Terminated"):
                ec = re.search(r"exit code: (0x[0-9A-Fa-f]+|-?\d+)", status)
                c["end"], c["status"] = when, "error"
                c["exit_code"] = ec.group(1) if ec else None
                c["detail"] = status
            else:
                c["detail"] = status
            continue

        cm = re.match(r"(?P<kw>\S+): Complete! \(commands took (?P<secs>\d+) seconds\)", msg)
        if cm:
            a = archives.setdefault(cm.group("kw"), {"event_type": "orc_archive", "archive": cm.group("kw"),
                                                     "status": "started"})
            a["commands_seconds"] = int(cm.group("secs"))
            a["commands_complete"] = True
            continue
        if msg.strip() == "JOB: Complete":
            job_complete += 1
            continue
        if lvl in ("W", "E", "C"):
            messages.append({"event_type": "orc_message", "ts": iso(ts), "level": LEVELS[lvl], "message": msg.strip()})

    # a command still "started" when the log stops was running when the log was copied
    for c in commands.values():
        c["ts"] = iso(c.get("start") or c.get("end"))
        c["start"], c["end"] = iso(c.get("start")), iso(c.get("end"))
        c["duration_seconds"] = seconds(c.get("start"), c.get("end"))
        if c["status"] == "started":
            c["status"] = "running when the log ends"
    expected = run["expected_archives"]
    for a in archives.values():
        a["ts"] = iso(a.get("start") or a.get("end"))
        a["start"], a["end"] = iso(a.get("start")), iso(a.get("end"))
    log_complete = job_complete >= len(expected) > 0
    for key in expected:
        if key not in archives:
            # absent from the log: never started if the log covers the whole run, otherwise the log
            # simply stops before it (it was copied while DFIR ORC was still running)
            archives[key] = {"event_type": "orc_archive", "archive": key, "ts": iso(last_ts),
                             "status": "not started" if log_complete else "after the end of the log"}
    # what the extraction actually holds is the ground truth for an archive, whatever the log says
    present = set()
    if extracted_dir and extracted_dir.is_dir():
        present = {p.name.lower() for p in extracted_dir.iterdir() if p.is_dir()}
    for a in archives.values():
        a["expected"] = a["archive"] in expected
        a["in_extraction"] = a["archive"].lower() in present if extracted_dir else None

    run.update({
        "log_name": path.name,
        "log_complete": log_complete,
        "archives_in_extraction": sorted(a["archive"] for a in archives.values() if a.get("in_extraction")),
        "archives_missing": sorted(a["archive"] for a in archives.values()
                                   if a["expected"] and a.get("in_extraction") is False),
        "ts": iso(run.get("start_time") or first_ts),
        "log_first": iso(first_ts), "log_last": iso(last_ts),
        "expected_archive_count": len(expected),
        "archives_complete": sum(1 for a in archives.values() if a.get("commands_complete")),
        "commands": len(commands),
        "commands_success": sum(1 for c in commands.values() if c["status"] == "success"),
        "commands_error": sum(1 for c in commands.values() if c["status"] == "error"),
        "commands_running": sum(1 for c in commands.values() if c["status"].startswith("running")),
        "user_elevated": "(elevated)" in run.get("user", ""),
        "run_complete": bool(expected) and all(archives.get(k, {}).get("commands_complete") for k in expected),
    })
    return [run] + list(archives.values()) + list(commands.values()) + messages


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input-dir", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    host = re.sub(r"^Endpoint_", "", args.input_dir.name)
    logs = sorted(args.input_dir.glob("DFIR-ORC_*.log"))
    if not logs:
        print(f"[orc_log] no DFIR-ORC_*.log in {args.input_dir}", file=sys.stderr)
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for log in logs:
        stamp = re.search(r"_(\d{8})_(\d{6})\.log$", log.name)
        suffix = "_".join(stamp.groups()) if stamp else datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out = args.output_dir / f"orc_log_{host}_{suffix}.jsonl"
        events = parse(log, args.input_dir / "extracted_files")
        with out.open("w", encoding="utf-8") as fh:
            for ev in events:
                fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
        print(f"[orc_log] {log.name}: {len(events)} events -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
