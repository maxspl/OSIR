from __future__ import annotations
import re
import json
from typing import List, Dict, Any, Optional


class ListDllsParser:
    """Parse Sysinternals listdlls output into structured JSONL records.

    The parser extracts the list of loaded DLLs (or EXEs) for each process.

    Parsing details:
        * Process headers look like: explorer.exe pid: 1234
        * Module table is detected via a header row containing "base", "size", and "path/module/file".
        * Module rows follow the pattern: <base>  <size>  <full_path>
        * Returns a JSONL string (newline-delimited JSON objects).
    """

    # Example: "notepad.exe         pid: 1234"
    _proc_header_re = re.compile(r"^(.+?)\s+pid:\s+(\d+)\b", re.IGNORECASE)

    # Example: "7FF6C5C40000  1B9000  C:\Windows\System32\shell32.dll"
    _module_line_re = re.compile(
        r"^(0x[0-9A-Fa-f]+|[0-9A-Fa-f]+)\s+"
        r"(0x[0-9A-Fa-f]+|[0-9A-Fa-f]+)\s+"
        r"(.+)$"
    )

    # Divider line (e.g. "-------------------")
    _dashed_re = re.compile(r"^-{5,}\s*$")

    # Ignore: "Error opening process ... "
    _error_opening_re = re.compile(r"^error\s+opening\b", re.IGNORECASE)

    # Ignore: Command line: ...
    _command_line_re = re.compile(r"^command\s+line:", re.IGNORECASE)

    def parse(self, text: str) -> str:
        """Parse raw listdlls text output and return JSONL records.

        Args:
            text: Full stdout text from Sysinternals listdlls.exe.

        Returns:
            A JSONL string where each line is a JSON object describing a single
            loaded module (DLL, EXE, etc.), annotated with its owning process.

        Example return line:
            {"type":"loaded_module","process_name":"notepad.exe","pid":"1234",...}
        """
        records: List[Dict[str, Any]] = []
        current_proc: Optional[Dict[str, Any]] = None
        parsing_modules = False

        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                parsing_modules = False
                continue

            # Skip divider lines or known useless rows
            if self._dashed_re.match(line):
                parsing_modules = False
                continue
            if self._error_opening_re.match(line):
                continue
            if self._command_line_re.match(line):
                continue

            # Process header
            m_proc = self._proc_header_re.match(line)
            if m_proc:
                current_proc = {
                    "process_name": m_proc.group(1).strip(),
                    "pid": m_proc.group(2),  # keep PID as string
                }
                parsing_modules = False
                continue

            # Detect the header of the module table (contains "base", "size", and path/module wording)
            if current_proc:
                header_norm = re.sub(r"\s+", " ", line.lower())
                if (
                    "base" in header_norm
                    and "size" in header_norm
                    and ("path" in header_norm or "module" in header_norm or "file" in header_norm)
                ):
                    parsing_modules = True
                    continue

            # Actual module lines
            if current_proc and parsing_modules:
                m_mod = self._module_line_re.match(line)
                if m_mod:
                    base = m_mod.group(1)
                    size = m_mod.group(2)
                    path = m_mod.group(3)
                    records.append({
                        "type": "loaded_module",
                        "process_name": current_proc.get("process_name"),
                        "pid": current_proc.get("pid"),
                        "base_address": base,
                        "size": size,
                        "path": path,
                    })
                    continue
                else:
                    # module table ended
                    parsing_modules = False

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
