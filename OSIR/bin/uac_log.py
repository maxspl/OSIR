#!/usr/bin/env python3
"""Parse the two logs UAC leaves with a collection into JSON Lines.

  uac-<host>-<os>-<timestamp>.log   the acquisition log, beside the archive: case information,
                                    acquisition start and finish, archive name and its hashes;
  extracted_files/uac.log           the execution log: version, command line and profile, the host
                                    as UAC saw it, the options, every artifact it parsed and every
                                    command it ran, the errors.

Events:
  uac_run       the collection as a whole: UAC version, profile, command line, account, host, time
                zone, artifacts selected, acquisition window (UTC), archive name / MD5 / SHA-1, case
                fields, commands run, errors, whether the log reaches the end of the collection;
  uac_artifact  one line per artifact file UAC parsed (`artifact_file`: OSIR stamps its own `artifact`
                field on every event): when, how long, how many commands it ran,
                how many wrote to stderr, how many errors;
  uac_error     the ERR lines.

    uac_log.py --input-dir <extract_uac/Endpoint_X> --output-dir <case>/uac_log

The output file is <host>--uac_log.jsonl, <host> taken from the Endpoint directory like every UAC module.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LINE = re.compile(r"^(?P<ts>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d [+-]\d{4}) (?P<lvl>[A-Z]{3}) (?P<msg>.*)$")
ACQ_TIME = ("%a %b %d %H:%M:%S %Y %z", "%a %b %d %H:%M:%S %Y")


def utc(ts, fmts=("%Y-%m-%d %H:%M:%S %z",)):
    for fmt in fmts:
        try:
            dt = datetime.strptime(ts.strip(), fmt)
        except (ValueError, AttributeError):
            continue
        if dt.tzinfo is None:
            return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z?"      # no offset in the log: not converted
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def seconds(a, b):
    try:
        f = "%Y-%m-%dT%H:%M:%SZ"
        return int((datetime.strptime(b, f) - datetime.strptime(a, f)).total_seconds())
    except (TypeError, ValueError):
        return None


def acquisition(path):
    """The key: value lines of the acquisition log, by section."""
    out, section = {}, ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        m = re.match(r"^Created by UAC \(Unix-like Artifacts Collector\)\s*(\S+)", s)
        if m:
            out["uac_version"] = m.group(1)
        if s.startswith("[") and s.endswith("]"):
            section = s[1:-1].lower()
            continue
        if ":" in s:
            k, v = s.split(":", 1)
            key = k.strip().lower().replace(" ", "_")
            out[key] = v.strip()
    fields = {
        "case_number": out.get("case_number"), "evidence_number": out.get("evidence_number"),
        "case_description": out.get("description"), "examiner": out.get("examiner"), "case_notes": out.get("notes"),
        "acquisition_started": utc(out.get("acquisition_started"), ACQ_TIME),
        "acquisition_finished": utc(out.get("acquisition_finished"), ACQ_TIME),
        "archive": out.get("file"), "archive_format": out.get("format"),
        "archive_md5": out.get("md5_checksum"), "archive_sha1": out.get("sha1_checksum"),
        "acq_hostname": out.get("hostname"), "acq_os": out.get("operating_system"),
        "acq_architecture": out.get("system_architecture"), "acq_mount_point": out.get("mount_point"),
    }
    if out.get("uac_version"):
        fields["uac_version"] = out["uac_version"]
    return {k: (v if v != "" else None) for k, v in fields.items()}


def execution(path):
    run, artifacts, errors = {}, [], []
    current = None
    first = last = None
    commands = stderr = 0
    completed_in = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(raw)
        if not m:
            continue
        ts, lvl, msg = utc(m.group("ts")), m.group("lvl"), m.group("msg")
        first = first or ts
        last = ts
        if lvl == "INF":
            km = re.match(r"^(?P<k>[A-Za-z][\w ()/-]*?):\s(?P<v>.*)$", msg)
            if msg.startswith("Unix-like Artifacts Collector"):
                run["uac_version"] = msg.split()[-1]
            elif msg.startswith("Parsing "):
                current = {"event_type": "uac_artifact", "artifact_file": msg[len("Parsing "):].strip(),
                           "ts": ts, "start": ts, "commands": 0, "commands_with_stderr": 0, "errors": 0}
                artifacts.append(current)
            elif re.match(r"^\d+ artifact\(s\) selected", msg):
                run["artifacts_selected"] = int(msg.split()[0])
            elif msg.startswith("Artifacts collection completed"):
                cm = re.search(r"in (\d+) seconds", msg)
                completed_in = int(cm.group(1)) if cm else None
            elif km and current is None:
                key = km.group("k").strip().lower().replace(" ", "_").replace("-", "_")
                if len(key) <= 40 and not key.startswith("find_") and "support" not in key:
                    run[key] = km.group("v").strip()
        elif lvl == "CMD":
            commands += 1
            has_err = " 2> " in msg
            stderr += has_err
            if current is not None:
                current["commands"] += 1
                current["commands_with_stderr"] += has_err
                current["end"] = ts
        elif lvl in ("ERR", "WRN"):
            errors.append({"event_type": "uac_error", "ts": ts, "level": "error" if lvl == "ERR" else "warning",
                           "artifact_file": current["artifact_file"] if current else None, "message": msg.strip()})
            if current is not None:
                current["errors"] += 1
    for a in artifacts:
        a["end"] = a.get("end") or a["start"]
        a["duration_seconds"] = seconds(a["start"], a["end"])
    cl = run.get("command_line", "")
    pm = re.search(r"(?:-p|--profile)\s+(\S+)", cl)
    am = re.search(r"(?:-a|--artifacts)\s+(\S+)", cl)
    run.update({
        "profile": pm.group(1) if pm else None, "artifacts_option": am.group(1) if am else None,
        "log_first": first, "log_last": last, "commands": commands, "commands_with_stderr": stderr,
        "errors": len(errors), "artifacts_parsed": len(artifacts),
        "collection_completed": completed_in is not None, "collection_seconds": completed_in,
    })
    return run, artifacts, errors


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input-dir", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    host = re.sub(r"^Endpoint_", "", args.input_dir.name)
    acq_logs = sorted(args.input_dir.glob("uac-*.log"))
    exe_log = args.input_dir / "extracted_files" / "uac.log"
    if not acq_logs and not exe_log.is_file():
        print(f"[uac_log] no UAC log in {args.input_dir}", file=sys.stderr)
        return 0
    run = {"event_type": "uac_run", "acquisition_log": acq_logs[-1].name if acq_logs else None,
           "execution_log": "uac.log" if exe_log.is_file() else None}
    artifacts, errors = [], []
    if exe_log.is_file():
        r, artifacts, errors = execution(exe_log)
        run.update(r)
    if acq_logs:
        run.update({k: v for k, v in acquisition(acq_logs[-1]).items() if v is not None or k not in run})
    run["ts"] = run.get("acquisition_started") or run.get("log_first")
    run["acquisition_seconds"] = seconds(run.get("acquisition_started"), run.get("acquisition_finished"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / f"{host}--uac_log.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for ev in [run] + artifacts + errors:
            fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
    print(f"[uac_log] {host}: {1 + len(artifacts) + len(errors)} events -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
