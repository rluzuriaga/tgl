import os
import subprocess
from time import sleep
from signal import SIG_DFL

import pexpect
from dotenv import load_dotenv

from tgl.config import DatabasePath

load_dotenv()


def remove_db_file() -> None:
    """ Function to remove a database file if it exists.
    This function uses the DatabasePath class from `tgl/config.py` to determine what
    database file to remove.
    """
    if os.path.exists(DatabasePath.get()):
        # Since the tests run faster than what Python can remove the file,
        #  the function is recursive to wait until the program actually lets
        #  go of the database before removing it.
        try:
            os.remove(DatabasePath.get())
        except PermissionError:
            sleep(0.01)
            remove_db_file()


def tgl_stop() -> None:
    """ Stop any timer that is running. """
    subprocess.run(['tgl', 'stop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def setup_credentials() -> None:
    cmd = pexpect.spawn('tgl setup -a')

    cmd.expect("Please enter your API token \(found under 'Profile settings' in the Toggl website\):")
    cmd.sendline(os.environ.get('API_KEY'))

    # Need to use this wait command instead of `cmd.expect(pexpect.EOF)` since sometimes the expected output
    #  is delayed because the application isn't disabling the echo quickly enough.
    # By using cmd.wait(), the function waits until the expected output is pexpect.EOF.
    cmd.wait()

    cmd.kill(SIG_DFL)
    cmd.close()


def run_command(command: str) -> str:
    cmd = pexpect.spawn(command)
    cmd.expect(pexpect.EOF)
    cmd.kill(SIG_DFL)
    cmd.close()

    return cmd.before.decode('utf-8')


def delete_project_with_name(project_name: str) -> None:
    cmd = pexpect.spawn('tgl delete project')
    cpl = cmd.compile_pattern_list([
        pexpect.EOF,
        rf'(?:\s*)(\d*)(?::\s*)({project_name})',
        'Please enter the number of the project you want to delete:'
    ])

    project_number = ""

    while True:
        i = cmd.expect_list(cpl, timeout=None)

        if i == 0:
            break
        elif i == 1:
            project_number = cmd.match.group(1).decode('utf-8')
            cmd.close
        elif i == 2:
            cmd.sendline(project_number)
            cmd.close

    cmd.wait()

    cmd.kill(SIG_DFL)
