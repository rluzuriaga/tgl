import os
import subprocess
from signal import SIG_DFL

import pexpect
from dotenv import load_dotenv

load_dotenv()


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
