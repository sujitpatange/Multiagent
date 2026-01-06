from datetime import datetime
from typing import List, Dict, Any
import json
import os

class AuditStore:
    def __init__(self, storage_path: str = "audit_log.jsonl"):
        self.storage_path = storage_path

    def log_event(self, event_type: str, data: Dict[str, Any]):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        with open(self.storage_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_logs(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.storage_path):
            return []
        logs = []
        with open(self.storage_path, "r") as f:
            for line in f:
                logs.append(json.loads(line))
        return logs
