from __future__ import annotations
import re
import json
from typing import List, Dict, Any, Optional


class WmiEventConsumerParser:
    """Parse WMI `EventConsumer` text blocks into structured JSONL.

    This parser ingests output similar to:

        Name                : ActiveScriptEventConsumer
        CreatorSID          : S-1-5-21-123...
        ScriptFileName      : C:\\Windows\\Temp\\evil.vbs
        ScriptingEngine     : VBScript
        KillTimeOut         : 0

    Blank lines delimit records. Duplicate keys are preserved by converting
    values into lists. Any unmatched lines are stored in `_raw_extra`.
    """

    _pair_re = re.compile(r"^\s*([^:]+?)\s*:\s*(.*)\s*$")

    def parse(self, text: str) -> str:
        """Convert raw WMI EventConsumer dump into JSONL records.

        Args:
            text: Raw text obtained from a command such as Get-WmiObject -Namespace root\\Subscription -Class __EventConsumer 

        Returns:
            A JSONL string where each line is a record like:

                {
                    "type": "wmi_eventconsumer",
                    "Name": "ActiveScriptEventConsumer",
                    "ScriptFileName": "C:\\Windows\\Temp\\evil.vbs",
                    "ScriptingEngine": "VBScript",
                    "KillTimeOut": "0"
                }
        """
        records: List[Dict[str, Any]] = []
        current: Optional[Dict[str, Any]] = None

        for line in text.splitlines():
            stripped = line.rstrip("\n")
            if stripped.strip() == "":
                if current:
                    current.setdefault("type", "wmi_eventconsumer")
                    records.append(current)
                    current = None
                continue

            m = self._pair_re.match(stripped)
            if not m:
                if current is None:
                    current = {}
                current.setdefault("_raw_extra", []).append(stripped.strip())
                continue

            key = m.group(1).rstrip()
            value_raw = m.group(2)  # raw, no coercion

            if current is None:
                current = {}

            if key in current:
                if isinstance(current[key], list):
                    current[key].append(value_raw)
                else:
                    current[key] = [current[key], value_raw]
            else:
                current[key] = value_raw

        if current:
            current.setdefault("type", "wmi_eventconsumer")
            records.append(current)

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
