from __future__ import annotations
import json
import re
from typing import List, Dict, Any

# Keys that BITS uses on single or mixed lines.
KNOWN_KEYS = [
    "GUID",
    "DISPLAY",
    "TYPE",
    "STATE",
    "OWNER",
    "PRIORITY",
    "FILES",
    "BYTES",
    "CREATION TIME",
    "MODIFICATION TIME",
    "COMPLETION TIME",
    "ACL FLAGS",
    "NOTIFY INTERFACE",
    "NOTIFICATION FLAGS",
    "RETRY DELAY",
    "NO PROGRESS TIMEOUT",
    "ERROR COUNT",
    "PROXY USAGE",
    "PROXY LIST",
    "PROXY BYPASS LIST",
    "ERROR FILE",
    "ERROR CODE",
    "ERROR CONTEXT",
    "DESCRIPTION",
    "JOB FILES",
    "NOTIFICATION COMMAND LINE",
    "owner MIC integrity level",
    "CUSTOM HEADERS",
]

KEY_ALT = "|".join(sorted(map(re.escape, KNOWN_KEYS), key=len, reverse=True))
PAIR_KEY_KNOWN = re.compile(rf"({KEY_ALT})\s*:", re.UNICODE)

JOBFILE_RE = re.compile(
    r"^\s*(\d+)\s*/\s*(\S+)\s+(\S+)\s+(https?://\S+)\s*->\s*(.+?)\s*$"
)


def _extract_pairs_known(line: str) -> Dict[str, str]:
    """Extract multiple `KEY: value` pairs from a single BITS line.

    BITS output often packs several key-value pairs on a single line, such as:
        TYPE: DOWNLOAD STATE: ERROR OWNER: DESKTOP\\User

    This helper only extracts pairs whose keys are in ``KNOWN_KEYS``.

    Args:
        line: Raw BITS output line.

    Returns:
        A dict mapping known BITS keys to their raw string values.
    """
    out: Dict[str, str] = {}
    matches = list(PAIR_KEY_KNOWN.finditer(line))
    for i, m in enumerate(matches):
        key = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(line)
        out[key] = line[start:end].strip()
    return out


class BitsJobsParser:
    """Parse ``bitsadmin`` output into structured JSONL job records.

    This parser:
      * Detects job boundaries using ``GUID:`` lines.
      * Handles multi-key lines (e.g. ``TYPE: ... STATE: ... OWNER: ...``).
      * Extracts peercaching flag blocks.
      * Parses ``JOB FILES`` indented entries as structured lists.
      * Converts ``owner elevated ?`` into a boolean.
      * Produces one JSON object per job, separated by newlines (JSONL format).
    """

    def parse(self, text: str) -> str:
        """Parse a full BITS job listing into JSONL.

        Args:
            text: Full textual output of `bitsadmin /list /verbose` or similar.

        Returns:
            A JSONL string, where each line is a JSON object representing a job.
        """
        records: List[Dict[str, Any]] = []
        current: Dict[str, Any] | None = None
        peercache_mode = False

        def commit() -> None:
            """Finalize the current job and append it to the output list."""
            nonlocal current
            if current:
                current["type"] = "bits_job"
                records.append(current)
                current = None

        for raw in text.splitlines():
            stripped = raw.strip()

            # Skip banners/footers
            if not stripped:
                peercache_mode = False
                continue
            if stripped.startswith(("BITSADMIN version", "BITS administration utility.", "(C) Copyright", "Listed ")):
                continue

            # New job starts at GUID
            if stripped.startswith("GUID:"):
                commit()
                current = {}
                current.update(_extract_pairs_known(stripped))
                continue

            if current is None:
                continue  # ignore lines before the first GUID

            # Peercaching flags block
            if stripped.startswith("Peercaching flags"):
                peercache_mode = True
                current.setdefault("Peercaching flags", {})
                continue

            if peercache_mode:
                if ":" in stripped:
                    k, v = stripped.split(":", 1)
                    current["Peercaching flags"][k.strip()] = v.strip()
                continue

            # JOB FILES entries (indented lines)
            m = JOBFILE_RE.match(stripped)
            if m:
                idx, unknown, working, url, dest = m.groups()
                lst = current.setdefault("JOB FILES LIST", [])
                lst.append(
                    {
                        "index": int(idx),
                        "status": f"{unknown} {working}".strip(),
                        "source": url,
                        "dest": dest,
                    }
                )
                continue

            # Odd line without colon: "owner elevated ?           false"
            if stripped.lower().startswith("owner elevated"):
                val = stripped.split()[-1].lower()
                current["owner elevated ?"] = val in ("true", "yes", "1")
                continue

            # Normal / multi-pair lines
            if ":" in stripped:
                pairs = _extract_pairs_known(stripped)
                if pairs:
                    current.update(pairs)
                continue

            # Fallback: stash raw
            current.setdefault("_raw", []).append(stripped)

        commit()
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
