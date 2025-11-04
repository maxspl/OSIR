from __future__ import annotations
import re
import json
from typing import List, Dict, Any


class DnsRecordsParser:
    """Parse DNS zone record listings into structured JSONL output.

    This parser is intended for command-line style DNS zone dumps that follow
    a pattern such as:

        *** example.com ***
        www     A     IN     3600    192.168.1.10
        mail    MX    IN     3600    10 mail.example.com

    Zones are detected by lines wrapped in `*** ... ***`.  
    Every subsequent non-comment line is parsed as a DNS record belonging to
    the current zone.

    Output format:
      - One JSON object per record.
      - Returned as JSONL (newline-separated JSON objects).
      - Fields are stored as raw strings (no type conversion).

    Example output record:

        {
            "type": "dns_record",
            "zone": "example.com",
            "name": "www",
            "record_type": "A",
            "field1": "IN",
            "field2": "3600",
            "ttl": "3600",
            "data": "192.168.1.10"
        }
    """

    _zone_header_re = re.compile(r"^\*\*\*\s*(.*?)\s*\*\*\*")

    def parse(self, text: str) -> str:
        """Parse a DNS zone record listing into JSONL.

        Args:
            text: Full raw output of a DNS zone listing command or file.

        Returns:
            A JSONL string where each line is a JSON object representing a
            single DNS record. Unknown or malformed lines are skipped.
        """
        records: List[Dict[str, Any]] = []
        current_zone: str | None = None

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # Detect new zone header: "*** example.com ***"
            m_zone = self._zone_header_re.match(line)
            if m_zone:
                current_zone = m_zone.group(1).strip()
                continue

            if line.startswith("*"):
                continue  # skip any other comment markers

            if current_zone is None:
                continue  # ignore entries before the first zone header

            parts = line.split()
            if len(parts) < 6:
                continue  # malformed line

            name = parts[0]
            record_type = parts[1]
            field1 = parts[2]
            field2 = parts[3]
            ttl = parts[4]
            data = " ".join(parts[5:])

            records.append({
                "type": "dns_record",
                "zone": current_zone,
                "name": name,
                "record_type": record_type,
                "field1": field1,
                "field2": field2,
                "ttl": ttl,
                "data": data,
            })

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
