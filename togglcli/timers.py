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

def current_timer(authentication: Tuple[str, str]) -> None:
    from datetime import datetime, timezone
    url = config['URI']['CURRENT']
    
    response = requests.get(
        url,
        auth=authentication
    )

    response_json = response.json()
    timer_description = response_json['data']['description']
    start_time = response_json['data']['start']
    
    # Since Python 3.6 is supported, the ':' in the timezone has to be removed from the time
    # This changed in Python 3.7 where %z can accept the ':' in the timezone
    if start_time[-3] == ':':
        start_time = start_time[:-3] + start_time[-2:]
    
    # Calculate how long the timer has been active
    start_time_object = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z')
    current_time_object = datetime.utcnow().replace(tzinfo=timezone.utc).replace(microsecond=0)
    running_time = current_time_object - start_time_object

    print("Current timer:")
    print(f"    Description:  {timer_description}")
    print(f"    Running time: {running_time}")
