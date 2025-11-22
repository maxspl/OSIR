from __future__ import annotations
import re
import json
from typing import List, Dict, Any


class NetstatParser:
    """Parse netstat -ano output (supports French/International variants).

    The parser extracts active TCP/UDP connections and emits one JSON object
    per row containing protocol, local/remote address, state, and PID.
    """

    def parse(self, text: str) -> str:
        """Parse raw netstat -ano text output into JSONL records.

        Args:
            text: Full output of netstat -ano (any language/locale).

        Returns:
            A single string containing one JSON object per line (JSONL format),
            each describing a network connection with fields:

                {
                    "type": "netstat_connection",
                    "protocol": "TCP",
                    "local_address": "192.168.0.10:49723",
                    "remote_address": "8.8.9.9:443",
                    "state": "ESTABLISHED",
                    "pid": "1216"
                }

        """
        records: List[Dict[str, Any]] = []
        lines = text.splitlines()
        parsing = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Detect the header row (e.g. "Proto Local Address ...")
            if stripped.lower().startswith("proto"):
                parsing = True
                continue

            if not parsing:
                continue

            if not stripped.startswith(("TCP", "UDP", "TCP6", "UDP6")):
                continue

            parts = re.split(r"\s+", stripped)
            if len(parts) < 5:
                continue

            protocol = parts[0]
            local_addr = parts[1]
            remote_addr = parts[2]
            state = parts[3]
            pid_str = parts[4]  # intentionally kept as string

            records.append({
                "type": "netstat_connection",
                "protocol": protocol,
                "local_address": local_addr,
                "remote_address": remote_addr,
                "state": state,
                "pid": pid_str,
            })

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
