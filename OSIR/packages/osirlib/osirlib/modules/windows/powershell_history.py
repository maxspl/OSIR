from __future__ import annotations
import os
import json
from typing import Dict, List, Any

from ...core.BaseModule import BaseModule
from ...core.PyModule import PyModule
from ...logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class PowerShellHistoryParser(PyModule):
    """
    Parse Windows Powershell history file.
    """

    def __init__(self, case_path: str, module: BaseModule) -> None:
        super().__init__(case_path, module)

    def __call__(self) -> bool:
        if self.module.input.type != "file":
            logger.error(f"Unsupported input type {self.module.input.type}")
            return False
        
        # Handle input file
        input_path = self.module.input.file
        if not input_path:
            logger.error("input.file is empty")
            return False
        
        # Read input (utf-8 with latin-1 fallback)
        try:
            with open(input_path, "r", encoding="utf-8") as fh:
                input_content = fh.read()
        except UnicodeDecodeError:
            with open(input_path, "r", encoding="latin-1") as fh:
                input_content = fh.read()

        # Parse
        records = self._parse_history(input_content) 

        # Construct output file
        out_path = None
        parts = os.path.normpath(input_path).split(os.sep)
        username = parts[parts.index("Users") + 1]

        try:
            self._format_output_file()
            out_path = os.path.join(self.default_output_dir, self.module.output.output_file)
            out_path = out_path.replace("username_changed_by_parser", username)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to prepare output path: {e}")
            return False

        # Write JSONL
        try:
            logger.debug(f"writing output to : {out_path}")
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.write(records)
        except Exception as e:
            logger.error(f"Failed to write JSONL '{out_path}': {e}")
            return False

        return True

    def _parse_history(self, input_content):
        records: List[Dict[str, Any]] = []

        for idx, line in enumerate(input_content.splitlines(), 1):
            cmd = line.strip()
            if not cmd:
                continue
            records.append({
                "type": "powershell_command",
                "line_number": str(idx),   # keeps positional context
                "command": cmd,
            })

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)