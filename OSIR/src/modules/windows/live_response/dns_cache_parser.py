from __future__ import annotations

import unicodedata
import re
import json
from typing import List, Dict, Any


def _normalise_key(key: str) -> str:
    """Normalize a DNS field name into a lowercase snake_case key.

    This helper removes punctuation, accents, and collapses whitespace:

        "Record Type."   -> "record_type"
        "Time To Live"   -> "time_to_live"
        "Réponse DNS"    -> "reponse_dns"

    Args:
        key: Raw field name extracted from the `ipconfig /displaydns` output.

    Returns:
        A normalized key suitable for use as a JSON field name.
    """
    key = key.strip().rstrip(".")
    nfkd = unicodedata.normalize("NFKD", key)
    without_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    without_punct = re.sub(r"[^\w\s]", "", without_accents)
    return re.sub(r"\s+", "_", without_punct).lower()


class DnsCacheParser:
    """Parse `ipconfig /displaydns` output into structured JSONL records.

    Each DNS cache block in the input becomes one JSON object with fields
    extracted from colon-separated lines (e.g. ``Record Name: example.com``).

    The parser:
      * Preserves the raw domain name as-is.
      * Normalizes field keys via ``_normalise_key``.
      * Leaves field values untouched (no type coercion).
      * Emits one JSON object per entry, separated by newlines (JSONL).

    Example record:

        {
            "type": "dns_cache_entry",
            "domain": "github.com",
            "record_type": "1",
            "time_to_live": "120",
            "data_length": "4",
            "section": "Answer"
        }
    """

    def parse(self, text: str) -> str:
        """Parse DNS cache text into a JSONL string.

        Args:
            text: Full output of ``ipconfig /displaydns`` or a similar dump.

        Returns:
            A JSONL string where each line is a JSON object describing a
            single DNS cache entry.
        """
        records: List[Dict[str, Any]] = []
        lines = text.splitlines()
        i, n = 0, len(lines)

        while i < n:
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith("---") or "Configuration" in line:
                i += 1
                continue

            # First non-empty line = domain name
            domain = line
            entry: Dict[str, Any] = {
                "type": "dns_cache_entry",
                "domain": domain,
            }
            i += 1

            # Skip separator lines
            while i < n and lines[i].strip().startswith("---"):
                i += 1

            # Parse key/value attributes until blank line
            while i < n and lines[i].strip():
                l2 = lines[i].strip()
                if ":" in l2:
                    key, value = l2.split(":", 1)
                    entry[_normalise_key(key)] = value.strip()
                i += 1

            records.append(entry)

            # Skip trailing blank lines before next record
            while i < n and not lines[i].strip():
                i += 1

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
