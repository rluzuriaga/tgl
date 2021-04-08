import os
import sys
import json
import requests
from typing import Tuple, List

from tgl import utils
from tgl.database import Database

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'config.json')

with open(config_file_path, 'r') as f:
    config = json.load(f)


def start_timer(description: str, authentication: Tuple[str, str],
                workspace_id: str, project_id: str, tags: List[str],
                billable: bool) -> None:
    url = Database().get_start_timer_url()

    header = {"Content-Type": "application/json", }
    data = {'time_entry': {
        'description': description,
        'wid': workspace_id,
        'pid': project_id,
        'tags': tags,
        'billable': billable,
        'created_with': 'tgl'}
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
    url = Database().get_current_timer_url()

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
    current_url = Database().get_current_timer_url()
    stop_url = Database().get_stop_timer_url()

    header = {"Content-Type": "application/json", }

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
            utils.add_paused_data_to_database(response.json())
            print(f'Timer "{timer_description}" paused.\nResume using "tgl resume".')
        else:
            utils.remove_previous_timer_from_config()
            print(f'Timer "{timer_description}" stopped.')
    else:
        sys.exit(f"ERROR: Timer could not be stopped. Response: {response.status_code}")


def resume_timer(authentication: Tuple[str, str]) -> None:
    paused_timer_data_tuple = Database().get_paused_timer()

    if len(paused_timer_data_tuple) == 0:
        sys.exit('There is no paused timer. Use "tgl start" to start a new timer.')

    url = Database().get_start_timer_url()

    header = {"Content-Type": "application/json", }

    workspace_id, description, project_id, billable, tags = paused_timer_data_tuple

    data = {'time_entry': {
        'description': description,
        'wid': workspace_id,
        'pid': "" if project_id is None else project_id,
        'tags': "" if tags is None else tags,
        'billable': bool(billable),
        'created_with': 'tgl'}
    }

    response = requests.post(
        url,
        headers=header,
        data=json.dumps(data),
        auth=authentication
    )

    if response.status_code == 200:
        print(f'Timer "{description}" resumed.')
        Database().set_paused_timer_as_resumed()
    else:
        sys.exit(f"ERROR: Timer could not be resumed. Response: {response.status_code}")


def create_project(authentication: Tuple[str, str], workspace_id: str, project_name: str) -> None:
    url = config['URI']['PROJECTS']
    header = {"Content-Type": "application/json", }

    data = {'project': {
        'name': project_name,
        'wid': workspace_id}
    }

    response = requests.post(
        url,
        headers=header,
        data=json.dumps(data),
        auth=authentication
    )

    workspace_name = config["WORKSPACES"][str(workspace_id)]

    if response.status_code == 200:
        print(f'\nProject "{project_name}" has been created in the "{workspace_name}" workspace.')
    else:
        # Can't strip("\n") when using f-strings so chr(10) is equivalent
        sys.exit(f'\nERROR: Project could not be created. \nResponse: "{response.text.strip(chr(10))}"')


def delete_project(authentication: Tuple[str, str]) -> None:
    deleting_pid = utils.get_project_id_from_user_selection()
    url = config['URI']['PROJECTS'] + f'/{deleting_pid}'

    response = requests.delete(
        url=url,
        auth=authentication
    )

    if response.status_code == 200:
        print(f'\nProject was deleted.')
    else:
        sys.exit(f'\nERROR: Project could not be deleted.\nResponse: "{response.text}"')
