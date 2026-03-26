import json
import os
from datetime import datetime

LOGS_FILE = os.path.join(os.path.dirname(__file__), "prompt_logs.json")


def _load_logs() -> list:
    if not os.path.exists(LOGS_FILE):
        return []
    with open(LOGS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_prompt_log(log_id: str, url: str, prompt_log: dict):
    logs = _load_logs()
    entry = {
        "log_id": log_id,
        "url": url,
        "timestamp": datetime.utcnow().isoformat(),
        **prompt_log
    }
    logs.append(entry)
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def get_all_logs() -> list:
    return _load_logs()