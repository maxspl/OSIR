from __future__ import annotations
import re
import json
from typing import List, Dict, Any


class RoutesParser:
    """Parse Windows route print output (supports localized output).

    The parser extracts:
      * Interface list
      * IPv4 routing table
      * IPv6 routing table

    Output is JSONL, one record per interface or route entry.
    """

    _iface_line_re = re.compile(r"^(\d+)\.\.\.\s*([0-9a-fA-F ]+)\s*\.{6}(.*)$")

    def parse(self, text: str) -> str:
        """Convert route print console output into JSONL records.

        Args:
            text: Full output of route print (any locale, typically French or English).

        Returns:
            A JSONL string where each line is one of:

            Interface entry:
                {
                    "type": "route_interface",
                    "index": "17",
                    "mac_address": "94 c6 91 12 a4 3b",
                    "name": "Intel(R) Ethernet I219-V"
                }

            IPv4 route:
                {
                    "type": "ipv4_route",
                    "destination": "0.0.0.0",
                    "netmask": "0.0.0.0",
                    "gateway": "192.168.1.1",
                    "interface": "192.168.1.42",
                    "metric": "25"
                }

            IPv6 route:
                {
                    "type": "ipv6_route",
                    "interface_index": "17",
                    "metric": "25",
                    "destination": "::/0",
                    "gateway": "fe80::1"
                }

        """
        records: List[Dict[str, Any]] = []
        lines = text.splitlines()
        state = None
        parsing_ipv4 = False
        parsing_ipv6 = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Section detection (localized)
            if stripped.startswith("Liste d'Interfaces"):
                state = "interfaces"
                continue
            if stripped.startswith("IPv4 Table de routage"):
                state = "ipv4"
                parsing_ipv4 = False
                continue
            if stripped.startswith("IPv6 Table de routage"):
                state = "ipv6"
                parsing_ipv6 = False
                continue

            # ---- Interface list ----
            if state == "interfaces":
                m_iface = self._iface_line_re.match(stripped)
                if m_iface:
                    index = m_iface.group(1)     # keep as string
                    mac_addr = " ".join(m_iface.group(2).split()).lower()
                    name = m_iface.group(3).strip()
                    records.append({
                        "type": "route_interface",
                        "index": index,
                        "mac_address": mac_addr,
                        "name": name,
                    })
                continue

            # ---- IPv4 routes ----
            if state == "ipv4":
                if not parsing_ipv4 and stripped.startswith("Destination"):
                    parsing_ipv4 = True
                    continue
                if parsing_ipv4:
                    if stripped.startswith(("====", "Itin", "Persistent")):
                        parsing_ipv4 = False
                        continue
                    parts = re.split(r"\s{2,}", stripped)
                    if len(parts) >= 5:
                        dest, mask, gateway, interface, metric = parts[:5]
                        records.append({
                            "type": "ipv4_route",
                            "destination": dest,
                            "netmask": mask,
                            "gateway": gateway,
                            "interface": interface,
                            "metric": metric,
                        })
                    continue

            # ---- IPv6 routes ----
            if state == "ipv6":
                if not parsing_ipv6 and stripped.startswith("If"):
                    parsing_ipv6 = True
                    continue
                if parsing_ipv6:
                    if stripped.startswith(("====", "Itin", "Persistent")):
                        parsing_ipv6 = False
                        continue
                    parts = re.split(r"\s{2,}", stripped)
                    if len(parts) >= 4:
                        iface_str, metric_str, dest, gateway = parts[:4]
                        records.append({
                            "type": "ipv6_route",
                            "interface_index": iface_str,
                            "metric": metric_str,
                            "destination": dest,
                            "gateway": gateway,
                        })
                    continue

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)