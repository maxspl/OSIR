from __future__ import annotations
import re
import json
from typing import List, Dict, Any, Optional


class HandleParser:
    """Parse Sysinternals handle.exe output into structured JSONL records.
    """

    # Example: "notepad.exe        pid: 1234  DESKTOP\\User"
    _proc_header_re = re.compile(r"^(.+?)\s+pid:\s+(\d+)\s+(.+)$", re.IGNORECASE)

    # Example: "  38: File  (RW-)   C:\\Windows\\Temp\\foo.txt"
    _handle_line_re = re.compile(
        r"^\s*([0-9A-Fa-f]+):\s+"        # handle ID in hex
        r"(\w+)"                         # handle type (File, Key, Mutant, etc.)
        r"(?:\s+\(([^)]*)\))?"           # optional rights "()"
        r"\s*(.*)$"                      # optional resource/name
    )

    def parse(self, text: str) -> str:
        """Parse raw handle.exe output into newline-delimited JSON.

        Args:
            text: Full stdout content from Sysinternals handle.exe.

        Returns:
            A JSONL string where each line is a JSON object describing a
            single open handle, enriched with the owning process context.

        Example return (one per line):
            {"type": "handle_entry", "process_name": "...", ... }
        """
        records: List[Dict[str, Any]] = []
        current_proc: Optional[Dict[str, Any]] = None

        for line in text.splitlines():
            line = line.rstrip()
            if not line:
                continue

            # Process header: "<exe> pid: 1234 <USERINFO>"
            m_proc = self._proc_header_re.match(line)
            if m_proc:
                current_proc = {
                    "process_name": m_proc.group(1).strip(),
                    "pid": m_proc.group(2),     # keep as string
                    "user": m_proc.group(3).strip(),
                }
                continue

            # Handle line: "  38: File (RW) C:\\Path"
            m_handle = self._handle_line_re.match(line)
            if m_handle:
                record: Dict[str, Any] = {
                    "type": "handle_entry",
                    "handle_id": m_handle.group(1),
                    "handle_type": m_handle.group(2),
                }
                rights = m_handle.group(3)
                name = m_handle.group(4).strip() if m_handle.group(4) else None
                if rights:
                    record["rights"] = rights
                if name:
                    record["name"] = name
                if current_proc:
                    record.update(current_proc)
                records.append(record)

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
