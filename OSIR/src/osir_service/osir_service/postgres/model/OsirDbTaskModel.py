from pydantic import BaseModel
from uuid import UUID
import re
from datetime import datetime
from typing import Literal, Dict, Any, Optional
from osir_service.postgres.model.OsirDbStatusModel import OsirDbStatusModel

class OsirDbTaskModel(BaseModel):
    task_id: UUID
    case_uuid: UUID
    agent: str
    module: str
    input: str
    output: Optional[str] = None
    processing_status: OsirDbStatusModel = OsirDbStatusModel.TASK_CREATED
    timestamp: datetime
    trace: Optional[Dict[str, Any]] = {}

    def get_logs(self) -> list:
        if not self.trace:
            return []
        
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        parsed = []

        for line in self.trace.get('logs', []):
            clean = ansi_escape.sub('', line)
            pattern = r'\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]\[([^\]]+)\]\s+-\s+(\S+)\s+-\s+(\S+)\s+-\s+(.*)'
            match = re.match(pattern, clean)

            if not match:
                parsed.append({"raw": line})
            else:
                parsed.append({
                    "level":     match.group(1),
                    "ts": match.group(2),
                    "msg":   f"{match.group(3)} {match.group(4).strip()} {match.group(5).strip()}",
                })

        return parsed