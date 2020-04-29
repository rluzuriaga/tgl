import json
import requests
from typing import Tuple

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

def add_defaults_to_config(authentication: Tuple[str, str]) -> None:
    url = config['URI']['USER_INFO']

    response = requests.get(url, auth=authentication)
    data = response.json()['data']

    config['DEFAULTS']['API_KEY'] = data['api_token']
    config['DEFAULTS']['WID'] = str(data['default_wid'])

    with open(config_file_path, 'w') as f:
        json.dump(config, f)

def are_defaults_empty() -> bool:
    if len(config['DEFAULTS']) == 0:
        return True
    return False

def delete_defaults() -> None:
    config['DEFAULTS'].clear()

    with open(config_file_path, 'w') as f:
        json.dump(config, f)

def auth_from_config() -> Tuple[str, str]:
    auth = (config['DEFAULTS']['API_KEY'], 'api_token')
    return auth