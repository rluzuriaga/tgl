import os
import sys
import argparse
from getpass import getpass

from tgl import utils
from tgl import timers
from tgl.config import DatabasePath
from tgl.database import Database


config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'config.json')


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
        prog='tgl',
        description='A command line interface for Toggl.'
    )

    parser.add_argument(
        '-d', required=False, metavar='Database Path', dest='database', nargs=1,
        help=f'Database file to use. Surround the database path with quotes. (default: {DatabasePath.get()})')

    commands_subparser = parser.add_subparsers(title='tgl commands', metavar='<command>', help='Command description')

    # tgl setup
    cmd_setup = commands_subparser.add_parser('setup', help='Configure the database with Toggl user data.')
    cmd_setup.set_defaults(func=command_setup)
    cmd_setup.add_argument('-a', '--api', required=False, dest='api', action='store_true',
                           default='', help='Use API key instead of username and password.')

    # tgl reconfig
    cmd_reconfig = commands_subparser.add_parser('reconfig', help='Reconfigure user data in the database.')
    cmd_reconfig.set_defaults(func=command_reconfig)

    # tgl start
    cmd_start = commands_subparser.add_parser('start', help='Start a Toggl timer.')
    cmd_start.set_defaults(func=command_start)
    cmd_start.add_argument('description', help='Timer description, use quotes around it unless it is one word.')
    cmd_start.add_argument('-p', '--project', required=False, dest='project',
                           action='store_true', help='Start timer in selected project.')
    cmd_start.add_argument(
        '-t', '--tags', required=False, dest='tags', default=[],
        nargs='*',
        help='Space seperated keywords that get saved as tags. If the tag is multiple words surround them in quotes.'
    )
    cmd_start.add_argument('-w', '--workspace', required=False, dest='workspace',
                           action='store_true', help='Select workspace to use for timer.')
    cmd_start.add_argument('-b', '--billable', required=False, dest='billable',
                           action='store_true', help='Set as billable hours. (For Toggl Pro members only).')

    # tgl current
    cmd_current = commands_subparser.add_parser('current', help='Get current timer.')
    cmd_current.set_defaults(func=command_current)

    # tgl stop
    cmd_stop = commands_subparser.add_parser('stop', help='Stop current timer.')
    cmd_stop.set_defaults(func=command_stop)

    # tgl pause
    cmd_pause = commands_subparser.add_parser('pause', help='Pause the current timer to resume later.')
    cmd_pause.set_defaults(func=command_pause)

    # tgl resume
    cmd_resume = commands_subparser.add_parser('resume', help='Resume a previously paused timer.')
    cmd_resume.set_defaults(func=command_resume)

    # tgl create
    cmd_create = commands_subparser.add_parser('create', help='Create new projects.')
    cmd_create.set_defaults(func=command_create)
    cmd_create.add_argument('request', choices=['project'], help='Create a new project.')
    cmd_create.add_argument('name', help='Name for the project.')

    # tgl delete
    cmd_delete = commands_subparser.add_parser('delete', help='Delete projects.')
    cmd_delete.set_defaults(func=command_delete)
    cmd_delete.add_argument('request', choices=['project'], help='Delete a project.')

    return parser


def command_setup(parser, args) -> None:
    # Check if the user entered a custom database and set it as the DatabasePath
    if args.database:
        DatabasePath.set(args.database[0])

    # If the defaults in the database are not empty ask if to reconfigure the user data
    if Database().is_user_data_saved():
        delete_data_input = input("User data is not empty. Do you want to reconfigure it? (y/N) ")

        if delete_data_input.lower() == 'y':
            Database().delete_user_data()
        else:
            sys.exit("Data was not changed.")

    print("    Configuring your account. Account information will be saved in plain text in")
    print(f"    the database located in {DatabasePath.get()}.\n")

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
        utils.add_user_data_to_database(auth)
    else:
        sys.exit("\nError: Incorrect credentials.")

    print("\nData saved.")


def command_reconfig(parser, args) -> None:
    # Check if the user entered a custom database and set it as the DatabasePath
    if args.database:
        DatabasePath.set(args.database[0])

    check_if_setup_is_needed()

    auth = Database().get_user_authentication()

    Database().delete_user_data()

    if utils.are_credentials_valid(auth):
        utils.add_user_data_to_database(auth)
        sys.exit("\nData reconfigured.")
    else:
        sys.exit("\nCredentials error. Please run 'tgl setup' to reconfigure the credential data.")


def command_start(parser, args) -> None:
    # Check if the user entered a custom database and set it as the DatabasePath
    if args.database:
        DatabasePath.set(args.database[0])

    check_if_setup_is_needed()

    authentication = Database().get_user_authentication()

    # Check if authentication is correct/api_key wasn't changed
    if not utils.are_credentials_valid(authentication):
        sys.exit("ERROR: Authentication error.\nRun 'tgl setup' to fully reconfigure the data.")

    # Check if there is already a timer running & give choice if there is
    if utils.is_timer_running(authentication):
        print("There is a timer currently running.")
        user_input = input("Do you want to stop the current timer and start a new one? (y/N): ")

        if user_input.lower() != 'y':
            sys.exit("\nCurrent timer not stopped. You can use 'tgl current' for more information of the current timer.")

    # Workspaces need to be checked first so that the project selection can be accurate
    if args.workspace:
        workspace_id: str = utils.workspace_selection()
    else:
        workspace_id = Database().get_default_workspace_id()

    # Check if user adds the project argument then calls a function to check
    # if there are projects in the users account then call the function that asks
    # the user what project to use.
    project_id = ""
    if args.project:
        if Database().are_there_projects():
            project_id = utils.project_selection(workspace_id)
        else:
            print("WARNING: You don't have any projects in your account.\n"
                  "  If you created one recently, please run 'tgl reconfig' to reconfigure your data.\n"
                  "  Timer will be crated without project.\n")

    timers.start_timer(
        description=args.description,
        authentication=authentication,
        workspace_id=workspace_id,
        project_id=project_id,
        tags=args.tags,
        billable=args.billable
    )


def command_current(parser, args) -> None:
    # Check if the user entered a custom database and set it as the DatabasePath
    if args.database:
        DatabasePath.set(args.database[0])

    check_if_setup_is_needed()

    authentication = Database().get_user_authentication()

    timers.current_timer(authentication)


def command_stop(parser, args) -> None:
    # Check if the user entered a custom database and set it as the DatabasePath
    if args.database:
        DatabasePath.set(args.database[0])

    check_if_setup_is_needed()

    authentication = Database().get_user_authentication()

    timers.stop_timer(authentication)


def command_pause(parser, args) -> None:
    check_if_setup_is_needed()

    authentication = utils.auth_from_config()

    timers.stop_timer(authentication, for_resume=True)


def command_resume(parser, args) -> None:
    check_if_setup_is_needed()

    authentication = utils.auth_from_config()

    # Check if there is already a timer running & give choice if there is
    if utils.is_timer_running(authentication):
        sys.exit('There is a timer currently running.')

    timers.resume_timer(authentication)


def command_create(parser, args) -> None:
    check_if_setup_is_needed()

    authentication = utils.auth_from_config()

    if args.request == 'project':
        workspace_id = utils.workspace_selection(verbose=False)

        timers.create_project(
            authentication=authentication,
            workspace_id=workspace_id,
            project_name=args.name
        )

    # Reconfigure the config file with new changes
    command_reconfig(parser, args)


def command_delete(parser, args) -> None:
    check_if_setup_is_needed()

    if not utils.are_there_projects():
        sys.exit(
            'There are no projects available in the config file.\nIf you recently '
            'added a project to your account, please use "tgl reconfig" to reconfigure your data.'
        )

    authentication = utils.auth_from_config()

    if args.request == 'project':
        timers.delete_project(
            authentication=authentication
        )

    command_reconfig(parser, args)


def check_if_setup_is_needed() -> None:
    if not Database().is_user_data_saved():
        sys.exit("Setup is not complete.\nPlease run 'tgl setup' before you can run a timer.")


if __name__ == "__main__":
    main(*sys.argv)
