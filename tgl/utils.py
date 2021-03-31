import os
import sys
import json
from typing import Tuple, Dict

from tgl.database import Database

import requests

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'config.json')

with open(config_file_path, 'r') as f:
    config = json.load(f)


def are_credentials_valid(authentication: Tuple[str, str]) -> bool:
    db = Database()

    url = db.get_user_info_url()

    response = requests.get(url, auth=authentication)

    if response.status_code == 200:
        return True

    return False


def _add_workspaces_to_database(authentication: Tuple[str, str]) -> None:
    db = Database()
    url = db.get_user_info_url()

    response = requests.get(url, auth=authentication)
    data = response.json()['data']

    for workspace in data['workspaces']:
        db.add_workspaces_data(workspace['id'], workspace['name'])


def _add_defaults_to_database(authentication: Tuple[str, str]) -> None:
    db = Database()

    url = db.get_user_info_url()

    response = requests.get(url, auth=authentication)
    data = response.json()['data']

    db.add_defaults_data(data['api_token'], data['default_wid'])


def _add_projects_to_database(authentication: Tuple[str, str]) -> None:
    db = Database()

    url_project = db.get_project_from_workspace_id_url()

    for wid in db.get_list_of_workspace_id_from_workspaces():
        url_project_wid = url_project.format(wid)

        response = requests.get(url_project_wid, auth=authentication)
        project_data = response.json()

        if project_data is not None:
            for project in project_data:
                db.add_projects_data(wid, project['id'], project['name'])


def add_user_data_to_database(authentication: Tuple[str, str]) -> None:
    # These functions need to be ran in this order because of foreign key restraints in the database
    _add_workspaces_to_database(authentication)
    _add_defaults_to_database(authentication)
    _add_projects_to_database(authentication)


def add_previous_timer_to_config(timer_data: dict) -> None:
    data = timer_data['data']

    config['PREVIOUS_TIMER']['wid'] = str(data['wid'])
    config['PREVIOUS_TIMER']['description'] = data['description']

    try:
        config['PREVIOUS_TIMER']['pid'] = str(data['pid'])
    except KeyError:
        config['PREVIOUS_TIMER']['pid'] = ""

    try:
        config['PREVIOUS_TIMER']['billable'] = data['billable']
    except KeyError:
        config['PREVIOUS_TIMER']['billable'] = ""

    try:
        config['PREVIOUS_TIMER']['tags'] = data['tags']
    except KeyError:
        config['PREVIOUS_TIMER']['tags'] = ""

    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4)


def remove_previous_timer_from_config():
    config['PREVIOUS_TIMER'].clear()

    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4)


def are_defaults_empty() -> bool:
    if len(config['DEFAULTS']) == 0:
        return True
    return False


def delete_user_data() -> None:
    config['DEFAULTS'].clear()
    config['PROJECTS'].clear()
    config['WORKSPACES'].clear()

    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4)


def auth_from_config() -> Tuple[str, str]:
    auth = (config['DEFAULTS']['API_KEY'], 'api_token')
    return auth


def are_there_projects() -> bool:
    if len(config['PROJECTS']) == 0:
        return False
    return True


def project_selection(workspace_id: str) -> str:
    print("\n0: Don't use any project")
    print("--------------------------")
    for i, project in enumerate(config['PROJECTS'][workspace_id].items()):
        print(str(i + 1) + f": {project[1]}")

    selection = input("\nPlease enter the number of the project you want to use: ")
    try:
        selection = int(selection) - 1
    except ValueError:
        sys.exit("\nERROR: Selection entered was not a number.")

    # Check if user entered 0 (Don't use any project)
    # If so, then project_id is ""
    # Else, try to get the project id from config
    if selection == -1:
        project_id = ""
    else:
        try:
            project_id = list(config['PROJECTS'][workspace_id].keys())[selection]
        except IndexError:
            sys.exit("\nERROR: Selection not valid. Timer not started.")

    return project_id


def is_timer_running(authentication: Tuple[str, str]) -> bool:
    url = config['URI']['CURRENT']

    response = requests.get(url, auth=authentication)
    response_json = response.json()

    if response_json['data'] is None:
        return False

    return True


def workspace_selection(verbose: bool = True) -> str:
    if len(config['WORKSPACES']) == 1:
        workspace_id = list(config['WORKSPACES'].keys())[0]
        if verbose:
            print("Only one workspace available in the config file.\nIf you recently "
                  "added a workspace on your account, please use 'tgl reconfig' to "
                  "reconfigure your data.\nUsing default workspace.")

        return workspace_id

    print()
    for i, workspace in enumerate(config['WORKSPACES'].items()):
        print(str(i + 1) + f": {workspace[1]}")

    selection = input("\nPlease enter the number of the workspace you want to use: ")
    try:
        selection = int(selection) - 1
    except ValueError:
        sys.exit("\nERROR: Selection entered was not a number.")

    try:
        workspace_id = list(config['WORKSPACES'].keys())[selection]
    except IndexError:
        sys.exit("\nERROR: Selection not valid. Timer not started.")

    return workspace_id


def get_default_workspace():
    return config['DEFAULTS']['WID']


def get_project_id_from_user_selection() -> str:
    all_project_dict = config['PROJECTS']
    selection_dict: Dict[str, str] = {}

    for i, project_dic in enumerate(all_project_dict.items(), start=1):
        wid: str = project_dic[0]
        workspace_name = config['WORKSPACES'][wid]

        workspace_output = f"Workspace: {workspace_name}"
        workspace_output = workspace_output + "\n" + ("-" * len(workspace_output))
        print(workspace_output)

        for pid, project_name in project_dic[1].items():
            selection_dict[str(i)] = pid
            print("    " + str(i) + ": " + project_name)

        print()

    user_selection = input("\nPlease enter the number of the project you want to delete: ")

    return selection_dict[user_selection]
