import json
from typing import Optional, Dict, Any
from pathlib import Path

CONFIG_FILE_NAME = "pydanticsql_config.json"

def get_config() -> Optional[Dict[str, Any]]:
    config_path = Path.cwd() / CONFIG_FILE_NAME
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return None
