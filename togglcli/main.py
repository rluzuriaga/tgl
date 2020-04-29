import sys
import argparse
from getpass import getpass
from typing import Tuple

from togglcli import utils
from togglcli import timers
from togglcli.defaults import get_default_config_file_path

config_file_path = get_default_config_file_path()

def main(file_name_junk, *argv) -> None:
    parser = create_parser()

    if len(argv) <= 0:
        parser.print_help()
        sys.exit()
    
    args = parser.parse_args(argv)
    args.func(parser, args)

def setuptools_entry() -> None:
    main(*sys.argv)

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='togglcli', 
        description='A command line interface for Toggl.'
    )

    commands_subparser = parser.add_subparsers(title='Commands', metavar='<commands>', help='commands')

    # togglcli setup
    cmd_setup = commands_subparser.add_parser('setup', 
        help='Setup the account information for Toggl.')
    cmd_setup.set_defaults(func=command_setup)
    cmd_setup.add_argument('-a', '--api', required=False, dest='api', action='store_true',
        default='', help='Use API key instead of username and password.'
    )

    # togglcli start
    cmd_start = commands_subparser.add_parser('start', help='Start a Toggl timer.')
    cmd_start.set_defaults(func=command_start)
    cmd_start.add_argument('description', 
        help='Timer description, use quotes around it unless it is one word.'
    )

    return parser

def command_setup(parser, args) -> None:
    # If the defaults in the config.json file are not empty ask if to reconfigure
    if not utils.are_defaults_empty():
        delete_data_input = input("User data is not empty. Do you want to reconfigure it? (y/N) ")

        if delete_data_input.lower() == 'y':
            utils.delete_defaults()
        else:
            sys.exit("Data was not changed.")

    print("    Configuring your account. Account information will be saved in plain text on")
    print(f"    a JSON file in {config_file_path}.\n")

    # Create authentication tuple either from email/password or API key
    if args.api:
        api_key = input("Please enter your API token (found under 'Profile settings' in the Toggl website):\n")

        auth = (api_key, 'api_token')
    else:
        email = input("Please enter your email address: ")
        password = getpass("Please enter your password: ")

        auth = (email, password)
    
    # Program exits if nothing was entered
    if len(auth[0]) == 0:
        sys.exit("\nNothing entered, closing program.")
    
    # Check if the credentials are valid and then save the defaults to config.json
    if utils.are_credentials_valid(auth):
        utils.add_defaults_to_config(auth)
    else:
        sys.exit("\nError: Incorrect credentials.")

    print("\nData saved.")

def command_start(parser, args) -> None:
    # Check if setup was already ran/if the API key is already saved
    if utils.are_defaults_empty():
        sys.exit("Setup is not complete.\nPlease run 'togglci setup' before you can run a timer.")
    
    authentication = utils.auth_from_config()

    # Check if authentication is correct/api_key wasn't changed
    if not utils.are_credentials_valid(authentication):
        sys.exit("ERROR: Authentication error.\nRun 'togglcli setup' to reconfigure the data.")
    
    timers.start_timer(
        description=args.description,
        authentication=authentication
    )

if __name__ == "__main__":
    main(*sys.argv)
