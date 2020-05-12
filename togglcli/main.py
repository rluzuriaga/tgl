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

    # togglcli reconfig
    cmd_reconfig = commands_subparser.add_parser('reconfig',
        help='Reconfigure data in config.json.')
    cmd_reconfig.set_defaults(func=command_reconfig)

    # togglcli start
    cmd_start = commands_subparser.add_parser('start', help='Start a Toggl timer.')
    cmd_start.set_defaults(func=command_start)
    cmd_start.add_argument('description', 
        help='Timer description, use quotes around it unless it is one word.'
    )
    cmd_start.add_argument('-p', '--project', required=False, dest='project',
        action='store_true', help='Start timer in select project.'
    )
    cmd_start.add_argument('-t', '--tags', required=False, dest='tags', default=[],
        nargs='*', help='Space seperated keywords that get saved as tags. If multiple words need to be used the surround them in quotes.'
    )
    cmd_start.add_argument('-w', '--workspace', required=False, dest='workspace',
        action='store_true', help='Select workspace to use for timer.')

    # togglcli current
    cmd_current = commands_subparser.add_parser('current', help='Get current timer.')
    cmd_current.set_defaults(func=command_current)

    # togglcli stop
    cmd_stop = commands_subparser.add_parser('stop', help='Stop current timer.')
    cmd_stop.set_defaults(func=command_stop)

    return parser

def command_setup(parser, args) -> None:
    # If the defaults in the config.json file are not empty ask if to reconfigure
    if not utils.are_defaults_empty():
        delete_data_input = input("User data is not empty. Do you want to reconfigure it? (y/N) ")

        if delete_data_input.lower() == 'y':
            utils.delete_user_data()
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
        utils.add_user_data_to_config(auth)
        utils.add_projects_to_config(auth)
    else:
        sys.exit("\nError: Incorrect credentials.")

    print("\nData saved.")

def command_reconfig(parser, args) -> None:
    check_if_setup_is_needed()

    auth = utils.auth_from_config()

    utils.delete_user_data()

    if utils.are_credentials_valid(auth):
        utils.add_user_data_to_config(auth)
        utils.add_projects_to_config(auth)
    else:
        sys.exit("\nError: Incorrect credentials.")

def command_start(parser, args) -> None:
    check_if_setup_is_needed()

    authentication = utils.auth_from_config()

    # Check if authentication is correct/api_key wasn't changed
    if not utils.are_credentials_valid(authentication):
        sys.exit("ERROR: Authentication error.\nRun 'togglcli setup' to reconfigure the data.")
    
    # Check if there is already a timer running & give choice if there is
    if utils.is_timer_running(authentication):
        print("There is a timer currently running.")
        user_input = input("Do you want to stop the current timer and start a new one? (y/N): ")

        if user_input != 'y':
            sys.exit("\nCurrent timer not stoped. You can use 'togglcli current' for more information of the current timer.")

    # Workspaces need to be checked first so that the project selection can be accurate
    if args.workspace:
        workspace_id = utils.workspace_selection()
    else:
        workspace_id = utils.get_default_workspace()

    # Check if user adds the project argument then calls a function to check
    # if there are projects in the users account then call the function that asks
    # the user what project to use.
    project_id = ""
    if args.project:
        if utils.are_there_projects():
            project_id = utils.project_selection(workspace_id)
        else:
            print("WARNING: You don't have any projects in your account.\n"
                "  If you created one recently, please run 'togglcli setup' to reconfigure your data.\n"
                "  Timer will be crated without project.\n")

    timers.start_timer(
        description=args.description,
        authentication=authentication,
        workspace_id=workspace_id,
        project_id=project_id,
        tags=args.tags
    )

def command_current(parser, args) -> None:
    check_if_setup_is_needed()
    
    authentication = utils.auth_from_config()

    timers.current_timer(authentication)

def command_stop(parser, args) -> None:
    check_if_setup_is_needed()
    
    authentication = utils.auth_from_config()

    timers.stop_timer(authentication)

def check_if_setup_is_needed() -> None:
    if utils.are_defaults_empty():
        sys.exit("Setup is not complete.\nPlease run 'togglcli setup' before you can run a timer.")

if __name__ == "__main__":
    main(*sys.argv)
