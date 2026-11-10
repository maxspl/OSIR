#!/usr/bin/env python3
"""Convert one Microsoft-Extractor-Suite output file (Microsoft 365 / Entra ID / Azure) into JSON Lines.

Microsoft-Extractor-Suite writes its acquisitions as pretty-printed JSON arrays (Unified Audit Log,
Entra ID sign-in and audit logs, Azure activity logs) or as CSV (message trace, mailbox rules, risky
users / detections, MFA, administrators, users, applications...). Both are turned into one JSON object
per line, the original fields left untouched, with two fields added:

  log_type   what the file holds, from its name (ual, entra_signin, entra_audit, azure_activity,
             message_trace, mailbox_rules, risky_detections, ...; `unknown` when not recognised);
  ts         the time of the event in UTC (%Y-%m-%dT%H:%M:%S.%fZ). For the inventories, which describe
             a state and not an event (users, administrators, MFA, rules, applications...), it is the
             time of the collection, read in the name of the file or of its directory.

    o365_extractor_suite.py --input <file.json|.jsonl|.csv> --output <file.jsonl> [--dedup-dir <dir>]

With --dedup-dir, an event already written by another file is not written again: collections that
overlap (the same period acquired twice, sign-in logs pulled again an hour later...) end up indexed once.
Two events are the same when all their original fields are equal (the pagination counters of the UAL,
ResultIndex and ResultCount, left aside), so a record Microsoft updated between two collections is kept
in both versions. The directory holds, per output file, the hashes of the events
it wrote: processing a file again gives the same output, and deleting an output frees its events.
The inventories are not deduplicated: the same row in two collections is the same state seen twice.

Notes:
  - the input is read as a stream: the size of the file does not matter;
  - in a CSV, empty cells are dropped and the cells holding JSON (AuditData, AdditionalInfo) are decoded;
  - the dates of a CSV follow the locale of the machine that ran the collection: day-first or
    month-first is decided per file from the values (day-first when nothing tells), and they are
    taken as UTC, which is what Graph and Exchange Online return.
"""
import argparse
import csv
import fcntl
import hashlib
import json
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

# (log_type, pattern on the file name, fields holding the event time - none for an inventory).
TYPES = [
    ("ual",                  r"^UAL-\d{14}-\d{14}\.|UnifiedAuditLog", ["CreationDate", "AuditData.CreationTime", "CreationTime", "createdDateTime"]),
    ("entra_signin",         r"SignInLogs",                 ["createdDateTime", "CreatedDateTime"]),
    ("entra_audit",          r"\d-AuditLogs\.",             ["activityDateTime", "ActivityDateTime"]),
    ("azure_directory_activity", r"DirectoryActivityLogs?\.", ["eventTimestamp", "activityDateTime"]),
    ("azure_activity",       r"ActivityLogs?\.",            ["eventTimestamp", "submissionTimestamp"]),
    ("message_trace",        r"-MTL\.",                     ["Received"]),
    ("risky_detections",     r"Risky(?:Events|Detections)", ["ActivityDateTime", "DetectedDateTime"]),
    ("risky_users",          r"RiskyUsers",                 ["RiskLastUpdatedDateTime"]),
    ("admin_audit",          r"AdminAuditLog",              ["RunDate", "CreationDate", "CreationTime"]),
    ("mailbox_audit",        r"mailboxAuditLog",            ["LastAccessed", "CreationDate", "CreationTime"]),
    ("mailbox_rules",        r"MailboxRules",               []),
    ("transport_rules",      r"TransportRules",             []),
    ("mfa_authentication_methods", r"AuthenticationMethods", []),
    ("mfa_user_registration", r"UserRegistrationDetails",   []),
    ("user_applications",    r"UserApplications",           []),
    ("oauth_permissions",    r"OAuthPermissions",           []),
    ("conditional_access",   r"ConditionalAccessPolic",     []),
    ("devices",              r"-Devices\.",                 []),
    ("admins",               r"Administrators?\.",          []),
    ("users",                r"-Users\.",                   []),
]
# For a file that is not recognised: the first of these fields that holds a date.
GENERIC_TS = ["CreationDate", "CreationTime", "createdDateTime", "activityDateTime", "eventTimestamp",
              "Received", "ActivityDateTime", "TimeGenerated", "timestamp", "Timestamp"]

ISO = re.compile(r"^(\d{4})-(\d\d)-(\d\d)[T ](\d\d):(\d\d):(\d\d)(?:[.,](\d+))?\s*(Z|[+-]\d\d:?\d\d)?$")
LOCAL = re.compile(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})[ T]+(\d{1,2}):(\d\d)(?::(\d\d))?\s*([AaPp]\.?[Mm]\.?)?$")
PS_DATE = re.compile(r"^/Date\((-?\d+)\)/$")                      # ConvertTo-Json of Windows PowerShell 5
COLLECTED = re.compile(r"(?<!\d)(\d{4})(\d\d)(\d\d)-?(?:(\d\d)(\d\d)(\d\d)?)?(?!\d)")
OUT_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def log_type(name):
    for kind, pattern, fields in TYPES:
        if re.search(pattern, name, re.IGNORECASE):
            return kind, fields
    return "unknown", GENERIC_TS


def get(record, path):
    for key in path.split("."):
        if not isinstance(record, dict):
            return None
        record = record.get(key)
    return record


def parse_ts(value, day_first=True):
    """A datetime in UTC, or None."""
    if isinstance(value, dict):                                   # a PowerShell DateTime serialised as an object
        value = value.get("DateTime") or value.get("value")
    if not isinstance(value, str):
        return None
    value = value.strip()
    try:
        m = ISO.match(value)
        if m:
            y, mo, d, h, mi, s, frac, tz = m.groups()
            dt = datetime(int(y), int(mo), int(d), int(h), int(mi), int(s),
                          int((frac or "0")[:6].ljust(6, "0")), tzinfo=timezone.utc)
            if tz and tz != "Z":
                sign = 1 if tz[0] == "+" else -1
                dt -= sign * timedelta(hours=int(tz[1:3]), minutes=int(tz[-2:]))
            return dt
        m = LOCAL.match(value)
        if m:
            a, b, y, h, mi, s, ampm = m.groups()
            d, mo = (a, b) if day_first else (b, a)
            h = int(h)
            if ampm:
                h = h % 12 + (12 if ampm[0] in "Pp" else 0)
            return datetime(int(y), int(mo), int(d), h, int(mi), int(s or 0), tzinfo=timezone.utc)
        m = PS_DATE.match(value)
        if m:
            return EPOCH + timedelta(milliseconds=int(m.group(1)))
    except (ValueError, OverflowError):
        pass
    return None


def is_day_first(values):
    """dd/MM or MM/dd, from the values of a CSV: the locale of the collecting machine decides."""
    am_pm = False
    for value in values:
        m = LOCAL.match(value.strip()) if isinstance(value, str) else None
        if not m:
            continue
        if int(m.group(1)) > 12:
            return True
        if int(m.group(2)) > 12:
            return False
        am_pm = am_pm or bool(m.group(7))
    return not am_pm


def collection_time(path):
    """When the file was collected: the timestamp of its name or of its directories, else its mtime."""
    day = None
    for part in [path.name] + [p.name for p in list(path.parents)[:3]]:
        for m in COLLECTED.finditer(part):
            y, mo, d, h, mi, s = m.groups()
            try:
                dt = datetime(int(y), int(mo), int(d), int(h or 0), int(mi or 0), int(s or 0), tzinfo=timezone.utc)
            except ValueError:
                continue
            if not 2010 <= dt.year <= 2100:
                continue
            if h is not None:
                return dt
            day = day or dt                                       # a date alone: kept if no part gives the time
    return day or datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def encoding_of(path):
    with path.open("rb") as fh:
        head = fh.read(4)
    if head.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if head.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"
    if len(head) == 4 and head[1] == 0 and head[3] == 0:          # UTF-16 LE without BOM
        return "utf-16-le"
    return "utf-8"


def iter_json(path, chunk_size=1 << 20):
    """The objects of a JSON array, or of a JSON Lines file, without loading the file."""
    decoder = json.JSONDecoder()
    skip = " \t\r\n,[]﻿"
    with path.open("r", encoding=encoding_of(path), errors="replace") as fh:
        buf, pos, eof = "", 0, False
        while True:
            while pos < len(buf) and buf[pos] in skip:
                pos += 1
            if pos >= len(buf):
                if eof:
                    return
                buf, pos = "", 0
            else:
                try:
                    obj, pos = decoder.raw_decode(buf, pos)
                    yield obj
                    continue
                except json.JSONDecodeError:
                    if eof:
                        raise ValueError(f"truncated or invalid JSON at the end of {path.name}")
                buf, pos = buf[pos:], 0
            chunk = fh.read(chunk_size)
            eof = not chunk
            buf += chunk


def unwrap(records):
    """The Graph envelope {"value": [...]}, when a file is one instead of the list itself."""
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("value"), list) and len(record) <= 3:
            yield from record["value"]
        else:
            yield record


def cell(value):
    if len(value) > 1 and value[0] in "[{" and value[-1] in "]}":
        try:
            return json.loads(value)
        except ValueError:
            pass
    return value


def iter_csv(path):
    csv.field_size_limit(sys.maxsize)
    with path.open("r", encoding=encoding_of(path), errors="replace", newline="") as fh:
        first = fh.readline()
        if not first.startswith("#TYPE"):                         # Export-Csv without -NoTypeInformation
            fh.seek(0)
            if fh.encoding == "utf-8-sig":
                fh.read(1)
        for row in csv.DictReader(fh):
            extra = row.pop(None, None)
            record = {k: cell(v) for k, v in row.items() if k and v not in (None, "")}
            if extra:
                record["_extra_columns"] = extra
            if record:
                yield record


KEY_SIZE = 16
# Position of the record in the answer of Search-UnifiedAuditLog: changes with every query, says nothing of the event.
PAGINATION = ("ResultIndex", "ResultCount")


def event_key(record):
    if any(k in record for k in PAGINATION):
        record = {k: v for k, v in record.items() if k not in PAGINATION}
    canonical = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.blake2b(canonical.encode("utf-8", "replace"), digest_size=KEY_SIZE).digest()


@contextmanager
def locked(path):
    """One file at a time compares itself to the others. Without lock support, go on unprotected."""
    with path.open("a") as fh:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX)
        except OSError as exc:
            print(f"[o365_extractor_suite] no lock on {path} ({exc}): deduplication not protected", file=sys.stderr)
        yield


def seen_elsewhere(keys_dir, own, out_dir):
    """The events the other output files hold. The index of an output that is gone is dropped."""
    seen = set()
    for index in keys_dir.glob("*.keys"):
        if index.name == own:
            continue
        if not (out_dir / index.name[:-len(".keys")]).is_file():
            index.unlink(missing_ok=True)
            continue
        data = index.read_bytes()
        seen.update(data[i:i + KEY_SIZE] for i in range(0, len(data) - KEY_SIZE + 1, KEY_SIZE))
    return seen


def drop_duplicates(tmp, dst, keys, keys_dir):
    """Remove from tmp the events another file already wrote, or this one twice. Returns how many stay."""
    own = keys_dir / (dst.name + ".keys")
    seen = seen_elsewhere(keys_dir, own.name, dst.parent)
    keep = []
    for key in keys:
        keep.append(key not in seen)
        seen.add(key)
    kept = [k for k, ok in zip(keys, keep) if ok]
    if len(kept) < len(keys):
        filtered = tmp.with_name(tmp.name + "2")
        with tmp.open("r", encoding="utf-8") as fin, filtered.open("w", encoding="utf-8") as fout:
            for line, ok in zip(fin, keep):
                if ok:
                    fout.write(line)
        filtered.replace(tmp)
    if kept:
        tmp.replace(dst)
        own_tmp = own.with_name(own.name + ".tmp")
        own_tmp.write_bytes(b"".join(kept))
        own_tmp.replace(own)
    else:
        tmp.unlink()
        dst.unlink(missing_ok=True)
        own.unlink(missing_ok=True)
    return len(kept)


def convert(src, dst, dedup_dir=None):
    kind, ts_fields = log_type(src.name)
    collected = collection_time(src)
    day_first = True
    if src.suffix.lower() == ".csv":
        records = list(iter_csv(src))                             # a CSV is read twice: its date order first
        day_first = is_day_first(get(r, f) for r in records for f in ts_fields)
    else:
        records = unwrap(iter_json(src))
    dedup = dedup_dir is not None and bool(ts_fields)             # events only, not the inventories
    keys = []
    total = undated = 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as out:
        for record in records:
            if not isinstance(record, dict):
                record = {"value": record}
            if isinstance(record.get("AuditData"), str):          # UAL exported as CSV or through Graph
                record["AuditData"] = cell(record["AuditData"])
            if dedup:
                keys.append(event_key(record))
            ts = None
            for field in ts_fields:
                ts = parse_ts(get(record, field), day_first)
                if ts:
                    break
            if ts is None:
                undated += bool(ts_fields)
                ts = collected
            event = {"log_type": kind, "ts": ts.strftime(OUT_FMT)}
            event.update((k, v) for k, v in record.items() if k not in event)
            out.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            total += 1
    duplicates = 0
    if not total:
        tmp.unlink()
    elif dedup:
        keys_dir = dedup_dir / kind
        keys_dir.mkdir(parents=True, exist_ok=True)
        with locked(dedup_dir / f"{kind}.lock"):
            kept = drop_duplicates(tmp, dst, keys, keys_dir)
        duplicates, total = total - kept, kept
    else:
        tmp.replace(dst)
    return kind, total, undated, duplicates


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--dedup-dir", type=Path, help="skip the events another file already wrote; index kept there")
    args = ap.parse_args()
    if not args.input.is_file():
        print(f"[o365_extractor_suite] not a file: {args.input}", file=sys.stderr)
        return 1
    try:
        kind, total, undated, duplicates = convert(args.input, args.output, args.dedup_dir)
    except (ValueError, OSError, csv.Error) as exc:
        print(f"[o365_extractor_suite] {args.input}: {exc}", file=sys.stderr)
        return 1
    dup = f", {duplicates} duplicates skipped" if duplicates else ""
    if not total:
        print(f"[o365_extractor_suite] {args.input.name}: no {'new ' if duplicates else ''}record, nothing written{dup}")
        return 0
    note = f" ({undated} without an event time, stamped with the collection time)" if undated else ""
    print(f"[o365_extractor_suite] {args.input.name}: {total} {kind} events{note}{dup} -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
