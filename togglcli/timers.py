import sys
import json
import requests
from typing import Tuple, List

from togglcli import utils
from togglcli.defaults import get_default_config_file_path

config_file_path = get_default_config_file_path()

with open(config_file_path, 'r') as f:
    config = json.load(f)

def start_timer(description: str, authentication: Tuple[str, str], 
                workspace_id: str, project_id: str, tags: List[str],
                billable: bool) -> None:
    url = config['URI']['START']

    header = {"Content-Type": "application/json",}
    data = {'time_entry': {
        'description': description, 
        'wid': workspace_id, 
        'pid': project_id, 
        'tags': tags,
        'billable': billable,
        'created_with': 'togglcli'}
    }

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

    # Check if there is a timer currently running
    if response_json['data'] is None:
        sys.exit("There is no timer currently running.")

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

def stop_timer(authentication: Tuple[str, str], for_resume: bool = False) -> None:
    current_url = config['URI']['CURRENT']
    stop_url = config['URI']['STOP']

    header = {"Content-Type": "application/json",}

    response = requests.get(
        current_url,
        auth=authentication
    )

    response_json = response.json()
    
    if response_json['data'] is None:
        sys.exit("There is no timer currently running.")

    timer_id = response_json['data']['id']
    timer_description = response_json['data']['description']

    stop_url = stop_url.format(timer_id)

    response = requests.put(
        stop_url,
        headers=header,
        auth=authentication
    )

    if response.status_code == 200:
        if for_resume:
            utils.add_previous_timer_to_config(response.json())
            print(f'Timer "{timer_description}" paused.\nResume using "togglcli resume".')
        else:
            utils.remove_previous_timer_from_config()
            print(f'Timer "{timer_description}" stoped.')
    else:
        sys.exit(f"ERROR: Timer could not be stopped. Response: {response.status_code}")

def resume_timer(authentication: Tuple[str, str]) -> None:
    if len(config['PREVIOUS_TIMER']) == 0:
        sys.exit('There is no paused timer. Use "togglecli start" to start a new timer.')
    
    url = config['URI']['START']

    header = {"Content-Type": "application/json",}

    description = config['PREVIOUS_TIMER']['description']
    workspace_id = config['PREVIOUS_TIMER']['wid']
    project_id = config['PREVIOUS_TIMER']['pid']
    tags = config['PREVIOUS_TIMER']['tags']
    billable = config['PREVIOUS_TIMER']['billable']

    data = {'time_entry': {
        'description': description, 
        'wid': workspace_id, 
        'pid': project_id, 
        'tags': tags,
        'billable': billable,
        'created_with': 'togglcli'}
    }

    response = requests.post(
        url,
        headers=header,
        data=json.dumps(data),
        auth=authentication
    )

    if response.status_code == 200:
        print(f'Timer "{description}" resumed.')
        utils.remove_previous_timer_from_config()
    else:
        sys.exit(f"ERROR: Timer could not be resumed. Response: {response.status_code}")
