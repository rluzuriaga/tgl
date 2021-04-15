import os
import sys
import json
from typing import Any, List, Optional, Tuple, Dict

from tgl.database import Database

import requests

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'config.json')

with open(config_file_path, 'r') as f:
    config = json.load(f)


def are_credentials_valid(authentication: Tuple[str, str]) -> bool:
    url = Database().get_user_info_url()

    response = requests.get(url, auth=authentication)

    if response.status_code == 200:
        return True

    return False


def _add_workspaces_to_database(authentication: Tuple[str, str]) -> None:
    url = Database().get_user_info_url()

    response = requests.get(url, auth=authentication)
    data = response.json()['data']

    for workspace in data['workspaces']:
        Database().add_workspaces_data(workspace['id'], workspace['name'])


def _add_defaults_to_database(authentication: Tuple[str, str]) -> None:
    url = Database().get_user_info_url()

    response = requests.get(url, auth=authentication)
    data = response.json()['data']

    Database().add_defaults_data(data['api_token'], data['default_wid'])


def _add_projects_to_database(authentication: Tuple[str, str]) -> None:
    url_project = Database().get_project_from_workspace_id_url()

    for wid in Database().get_list_of_workspace_ids():
        url_project_wid = url_project.format(wid)

        response = requests.get(url_project_wid, auth=authentication)
        project_data = response.json()

        if project_data is not None:
            for project in project_data:
                Database().add_projects_data(str(wid), str(project['id']), project['name'])


def add_user_data_to_database(authentication: Tuple[str, str]) -> None:
    # These functions need to be ran in this order because of foreign key restraints in the database
    _add_workspaces_to_database(authentication)
    _add_defaults_to_database(authentication)
    _add_projects_to_database(authentication)


def add_paused_data_to_database(timer_data: Dict[Any, Any]) -> None:
    data = timer_data['data']

    workspace_id = str(data['wid'])
    description = data['description']

    project_id: Optional[str]
    try:
        project_id = str(data['pid'])
    except KeyError:
        project_id = None

    billable = data['billable']

    tags: Optional[List[str]]
    try:
        tags = data['tags']
    except KeyError:
        tags = None

    Database().add_paused_timer_data(workspace_id, description, project_id, billable, tags)


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

    project_dict = {}
    for i, project in enumerate(Database().get_list_of_project_names_from_workspace(workspace_id), start=1):
        print(str(i) + f": {project}")
        project_dict[i] = project

    selection = input("\nPlease enter the number of the project you want to use: ")
    try:
        selection_int = int(selection)
    except ValueError:
        sys.exit("\nERROR: Selection entered was not a valid number.")

    # Check if user entered 0 (Don't use any project)
    # If so, then project_id is ""
    # Else, try to get the project id from config
    if selection_int == 0:
        project_id = ""
    else:
        try:
            project_id = Database().get_project_id_from_project_name(project_dict[selection_int])
        except IndexError:
            sys.exit("\nERROR: Selection not valid. Timer not started.")

    return project_id


def is_timer_running(authentication: Tuple[str, str]) -> bool:
    url = Database().get_current_timer_url()

    response = requests.get(url, auth=authentication)
    response_json = response.json()

    if response_json['data'] is None:
        return False

    return True


def workspace_selection(verbose: bool = True) -> str:
    # Check if there is only one workspace
    # If there is only one workspace then a message is given to the user
    #  and the default workspace id is returned
    if len(Database().get_list_of_workspace_ids()) == 1:
        workspace_id: str = Database().get_default_workspace_id()
        if verbose:
            print("Only one workspace available in the config file.\nIf you recently "
                  "added a workspace on your account, please use 'tgl reconfig' to "
                  "reconfigure your data.\nUsing default workspace.")

        return workspace_id

    print()
    workspace_dict = {}
    for i, workspace in enumerate(Database().get_list_of_workspace_names(), start=1):
        print(str(i) + f": {workspace}")
        workspace_dict[i] = workspace

    selection = input("\nPlease enter the number of the workspace you want to use: ")
    try:
        selection_int = int(selection)
    except ValueError:
        sys.exit("\nERROR: Selection entered was not a valid number.")

    try:
        workspace_id = Database().get_workspace_id_from_workspace_name(
            workspace_dict[selection_int]
        )
    except IndexError:
        sys.exit("\nERROR: Selection not valid. Timer not started.")

    return workspace_id


def get_default_workspace():
    return config['DEFAULTS']['WID']


def get_project_id_from_user_selection() -> str:
    projects_list = Database().get_projects_from_all_workspaces()

    project_title_length = len(max([i[1] for i in projects_list], key=len)) + 14
    workspace_title_length = len(max([i[0] for i in projects_list], key=len)) + 2

    print("PROJECT NAME".center(project_title_length), end='  ')
    print("WORKSPACE NAME".center(workspace_title_length))
    print("-" * (workspace_title_length + project_title_length))

    selection_dict: Dict[int, str] = {}
    for i, (project_name, workspace_name, project_id) in enumerate(projects_list, start=1):
        print(f" {i}: {project_name.ljust(project_title_length)}{workspace_name}")
        selection_dict[i] = project_id

    user_selection = input("\nPlease enter the number next to the project you want to delete: ")

    try:
        user_selection_int = int(user_selection)
        selected_project_id = selection_dict[user_selection_int]
    except (ValueError, KeyError):
        sys.exit("\nERROR: Selection not valid. No project deleted.")

    return selected_project_id
