from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional


class RoutesParser:
    """Parse Windows `route print` output (supports localized output).

    Extracts:
      - Interface list
      - IPv4 routing table (active)
      - IPv6 routing table (active)

    Output is JSONL, one record per interface or route entry.
    """

    _iface_line_re = re.compile(r"^(\d+)\.\.\.\s*([0-9a-fA-F ]+)\s*\.{6}(.*)$")

    # Section header detection (EN + FR)
    _interfaces_hdr_re = re.compile(r"^(Interface List|Liste d'Interfaces)\b", re.I)
    _ipv4_hdr_re = re.compile(r"^(IPv4 Route Table|IPv4 Table de routage)\b", re.I)
    _ipv6_hdr_re = re.compile(r"^(IPv6 Route Table|IPv6 Table de routage)\b", re.I)

    # Table header detection
    _ipv4_cols_re = re.compile(r"^(Network Destination|Destination)\b", re.I)
    _ipv6_cols_re = re.compile(r"^If\s+Metric\s+Network Destination\s+Gateway\b", re.I)

    def parse(self, text: str) -> str:
        records: List[Dict[str, Any]] = []
        lines = text.splitlines()

        state: Optional[str] = None
        parsing_ipv4 = False
        parsing_ipv6 = False

        # For IPv6 wrapped lines: if gateway appears on next line
        pending_ipv6: Optional[Dict[str, str]] = None

        for raw in lines:
            stripped = raw.strip()
            if not stripped:
                continue

            # ---- Section detection (EN + FR) ----
            if self._interfaces_hdr_re.match(stripped):
                state = "interfaces"
                parsing_ipv4 = parsing_ipv6 = False
                pending_ipv6 = None
                continue

            if self._ipv4_hdr_re.match(stripped):
                state = "ipv4"
                parsing_ipv4 = False
                parsing_ipv6 = False
                pending_ipv6 = None
                continue

            if self._ipv6_hdr_re.match(stripped):
                state = "ipv6"
                parsing_ipv6 = False
                parsing_ipv4 = False
                pending_ipv6 = None
                continue

            # Separator lines reset nothing but are safe to skip
            if stripped.startswith("===="):
                continue

            # ---- Interface list ----
            if state == "interfaces":
                m_iface = self._iface_line_re.match(stripped)
                if m_iface:
                    index = m_iface.group(1)
                    mac_addr = " ".join(m_iface.group(2).split()).lower()
                    name = m_iface.group(3).strip()
                    records.append(
                        {
                            "type": "route_interface",
                            "index": index,
                            "mac_address": mac_addr,
                            "name": name,
                        }
                    )
                continue

            # ---- IPv4 routes ----
            if state == "ipv4":
                # Start when we hit the column header line
                if not parsing_ipv4 and self._ipv4_cols_re.match(stripped):
                    parsing_ipv4 = True
                    continue

                if parsing_ipv4:
                    # Stop when persistent routes section begins (EN/FR)
                    if stripped.lower().startswith(("persistent routes", "itinéraires persistants")):
                        parsing_ipv4 = False
                        continue
                    if stripped.lower().startswith(("active routes", "itinéraires actifs")):
                        # It's just a label line; keep parsing until persistent
                        continue

                    parts = re.split(r"\s{2,}", stripped)
                    if len(parts) >= 5:
                        dest, mask, gateway, interface, metric = parts[:5]
                        records.append(
                            {
                                "type": "ipv4_route",
                                "destination": dest,
                                "netmask": mask,
                                "gateway": gateway,
                                "interface": interface,
                                "metric": metric,
                            }
                        )
                continue

            # ---- IPv6 routes ----
            if state == "ipv6":
                # Start when we hit the IPv6 columns header
                if not parsing_ipv6 and self._ipv6_cols_re.match(stripped):
                    parsing_ipv6 = True
                    continue

                if parsing_ipv6:
                    # Stop when persistent routes section begins (EN/FR)
                    if stripped.lower().startswith(("persistent routes", "itinéraires persistants")):
                        parsing_ipv6 = False
                        pending_ipv6 = None
                        continue
                    if stripped.lower().startswith(("active routes", "itinéraires actifs")):
                        continue

                    # Handle wrapped gateway lines:
                    # Example:
                    #   4    281 fe80::.../128
                    #                                     On-link
                    if pending_ipv6 is not None:
                        # If line contains a single token like "On-link" or "fe80::1", treat as gateway
                        gw_parts = re.split(r"\s{2,}", stripped)
                        if len(gw_parts) == 1:
                            pending_ipv6["gateway"] = gw_parts[0]
                            records.append(pending_ipv6)
                            pending_ipv6 = None
                            continue
                        else:
                            # Something else; flush what we have with empty gateway to avoid losing it
                            pending_ipv6.setdefault("gateway", "")
                            records.append(pending_ipv6)
                            pending_ipv6 = None
                            # fall through to parse current line normally

                    parts = re.split(r"\s{2,}", stripped)

                    if len(parts) >= 4:
                        iface_str, metric_str, dest, gateway = parts[:4]
                        records.append(
                            {
                                "type": "ipv6_route",
                                "interface_index": iface_str,
                                "metric": metric_str,
                                "destination": dest,
                                "gateway": gateway,
                            }
                        )
                        continue

                    # If we have 3 columns, assume gateway is wrapped to next line
                    if len(parts) == 3:
                        iface_str, metric_str, dest = parts
                        pending_ipv6 = {
                            "type": "ipv6_route",
                            "interface_index": iface_str,
                            "metric": metric_str,
                            "destination": dest,
                            "gateway": "",
                        }
                        continue

                continue

        # Flush any pending IPv6 row if file ended unexpectedly
        if pending_ipv6 is not None:
            records.append(pending_ipv6)

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)