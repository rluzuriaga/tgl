import sys
import json
import requests
from typing import Tuple

from togglcli import timers
from togglcli.defaults import get_default_config_file_path

config_file_path = get_default_config_file_path()

with open(config_file_path, 'r') as f:
    config = json.load(f)

def are_credentials_valid(authentication: Tuple[str, str]) -> bool:    
    url = config['URI']['USER_INFO']

    response = requests.get(url, auth=authentication)

    if response.status_code == 200:
        return True
    
    return False

def add_user_data_to_config(authentication: Tuple[str, str]) -> None:
    url = config['URI']['USER_INFO']

    response = requests.get(url, auth=authentication)
    data = response.json()['data']

    config['DEFAULTS']['API_KEY'] = data['api_token']
    config['DEFAULTS']['WID'] = str(data['default_wid'])

    # Add WORKSPACES
    workspaces_dict = dict()
    for workspace in data['workspaces']:
        workspaces_dict.update({str(workspace['id']):workspace['name']})
    
    config['WORKSPACES'] = workspaces_dict

    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4)

def add_projects_to_config(authentication: Tuple[str, str]) -> None:
    url_project = config['URI']['PROJECTS_FROM_WID']

    for wid in config['WORKSPACES']:
        url_project_wid = url_project.format(wid)
    
        response = requests.get(url_project_wid, auth=authentication)
        project_data = response.json()

        if project_data is not None:
            projects_dict = dict({wid: {}})
            for project in project_data:
                projects_dict[wid].update({str(project['id']): project['name']})
        
            config['PROJECTS'].update(projects_dict)
            
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
    for i, project in enumerate(config['PROJECTS'][workspace_id].items()):
        print(str(i + 1) + f": {project[1]}")

    selection = input("Please enter the number of the project you want to use: ")
    try:
        selection = int(selection) - 1
    except ValueError:
        sys.exit("\nERROR: Selection entered was not a number.")

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

def workspace_selection() -> str:
    if len(config['WORKSPACES']) == 1:
        workspace_id = list(config['WORKSPACES'].keys())[0]
        print("Only one workspace available in the config file.\nIf you recently "
            "added a workspace on your account, please use 'togglcli setup' to "
            "reconfigure your data.\nUsing default workspace.\n")
        
        return workspace_id
    
    for i, workspace in enumerate(config['WORKSPACES'].items()):
        print(str(i + 1) + f": {workspace[1]}")
    
    selection = input("Please enter the number of the workspace you want to use: ")
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