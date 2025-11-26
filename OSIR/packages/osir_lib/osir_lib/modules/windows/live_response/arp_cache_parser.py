from __future__ import annotations

import re
import unicodedata
import json
from typing import List, Dict, Any


class ArpCacheParser:
    """Parse ARP cache output into structured records.

    This parser is **locale-agnostic**: it does not depend on English labels
    such as `dynamic`, `static`, etc. It only validates fields based on
    detectable patterns (IPv4, MAC, "incomplete" entries, etc.).

    Output format:
      -Each ARP entry becomes a JSON object.
      -The final result is returned as a **JSONL string** (one JSON per line).
      -Each record has the fixed type `"arp_entry"`.

    Supported input format:
      Typical `arp -a` or `arp -a -v` output, where entries follow an interface
      header such as:

          Interface: 192.168.1.10 --- 0x12
            192.168.1.1          11-22-33-44-55-66     dynamic
            192.168.1.42         incomplete

    The parser extracts:
      -Interface IP
      -Interface index (hex, string form)
      -IP address
      -MAC address (or "incomplete")
      -Entry type (raw string if present)

    """

    _interface_re = re.compile(
        r"^\s*.*?\b(\d{1,3}(?:\.\d{1,3}){3})\s+---\s+(\S+)\s*$"
    )
    _ipv4_re = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
    _mac_like_re = re.compile(
        r"^(?:[0-9A-Fa-f]{2}([-:])){5}[0-9A-Fa-f]{2}$|^(?:incomplete|incomplet|incompleto)$",
        re.IGNORECASE,
    )

    @staticmethod
    def _normalize_text(s: str) -> str:
        """Return a lowercase ASCII-normalized version of a string.

        Unicode accents are removed via NFKD normalization.  
        Currently unused, but kept for potential localization handling.

        Args:
            s: Input text.

        Returns:
            A normalized lowercase string with combining characters stripped.
        """
        return "".join(
            c for c in unicodedata.normalize("NFKD", s.lower())
            if not unicodedata.combining(c)
        )

    def parse(self, text: str) -> str:
        """Parse ARP cache text into JSONL.

        Args:
            text: Raw textual output from an ARP command (e.g. `arp -a`).

        Returns:
            A JSONL string where each line is a JSON object describing a single entry.
            Example object:

            {
                "type": "arp_entry",
                "interface_ip": "192.168.1.10",
                "interface_index": "0x12",
                "ip_address": "192.168.1.1",
                "mac_address": "11-22-33-44-55-66",
                "entry_type": "dynamic"
            }
        """
        records: List[Dict[str, Any]] = []
        current_iface_ip = None
        current_iface_index = None

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            m_iface = self._interface_re.match(line)
            if m_iface:
                current_iface_ip = m_iface.group(1)
                current_iface_index = m_iface.group(2)
                continue

            if not (current_iface_ip and current_iface_index):
                continue

            parts = re.split(r"\s{2,}", line)
            if len(parts) < 2:
                continue

            ip_candidate = parts[0]
            mac_candidate = parts[1]
            type_candidate = parts[2] if len(parts) >= 3 else ""

            if not self._ipv4_re.match(ip_candidate):
                continue
            if not self._mac_like_re.match(mac_candidate):
                continue

            records.append({
                "type": "arp_entry",
                "interface_ip": current_iface_ip,
                "interface_index": current_iface_index,
                "ip_address": ip_candidate,
                "mac_address": mac_candidate,
                "entry_type": type_candidate or "",
            })

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
