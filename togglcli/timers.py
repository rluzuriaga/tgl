import sys
import json
import requests
from typing import Tuple

from togglcli.defaults import get_default_config_file_path

config_file_path = get_default_config_file_path()

with open(config_file_path, 'r') as f:
    config = json.load(f)

def start_timer(description: str, authentication: Tuple[str, str]) -> None:
    url = config['URI']['START']
    workspace_id = config['DEFAULTS']['WID']

    header = {"Content-Type": "application/json",}
    data = {'time_entry': {'description': description, 'wid': workspace_id, 'created_with': 'togglcli'}}

    response = requests.post(
        url,
        headers=header,
        data=json.dumps(data),
        auth=authentication
    )

    if response.status_code == 200:
        print("Timer started.")
    else:
        sys.exit(f"ERROR: Timer not started. Response: {response.status_code}")
