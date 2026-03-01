from __future__ import annotations
import csv
import json
from typing import List, Dict, Any


class TcpvconParser:
    """Parse Sysinternals `tcpvcon -accepteula -n -c` CSV output.

    Sysinternals tcpvcon can export active TCP/UDP connections in CSV format.
    This parser expects that format and converts each row into a JSON object.
    """

    def parse(self, text: str) -> str:
        """Convert tcpvcon CSV output into JSONL records.

        Args:
            text: Raw CSV text as produced by `tcpvcon -c` (header is optional).

        Returns:
            A JSONL string where each line is a JSON object like:

                {
                    "type": "tcpvcon_connection",
                    "protocol": "TCP",
                    "process_name": "chrome.exe",
                    "pid": "1284",
                    "state": "ESTABLISHED",
                    "local_address": "192.168.1.42:49723",
                    "remote_address": "52.109.76.14:443"
                }
        """
        records: List[Dict[str, Any]] = []
        reader = csv.reader(line for line in text.splitlines() if line.strip())

        for row in reader:
            if len(row) < 6:
                continue

            protocol, process_name, pid_str, state, local_addr, remote_addr = (
                item.strip() for item in row[:6]
            )

            records.append({
                "type": "tcpvcon_connection",
                "protocol": protocol,
                "process_name": process_name,
                "pid": pid_str,
                "state": state,
                "local_address": local_addr,
                "remote_address": remote_addr,
            })

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
