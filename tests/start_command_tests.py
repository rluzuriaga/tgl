import os
import unittest
import subprocess
from signal import SIG_DFL

import pexpect
from dotenv import load_dotenv

from tgl.utils import delete_user_data

load_dotenv()


class TestStartCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        self._setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        # Stop any timer that was started in the tests
        subprocess.run(['tgl', 'stop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        delete_user_data()
        return super().tearDown()

    @staticmethod
    def _setup_credentials() -> None:
        cmd = pexpect.spawn('tgl setup -a')

        cmd.expect("Please enter your API token \(found under 'Profile settings' in the Toggl website\):")
        cmd.sendline(os.environ.get('API_KEY'))

        # Need to use this wait command instead of `cmd.expect(pexpect.EOF)` since sometimes the expected output
        #  is delayed because the application isn't disabling the echo quickly enough.
        # By using cmd.wait(), the function waits until the expected output is pexpect.EOF.
        cmd.wait()

        cmd.kill(SIG_DFL)
        cmd.close()

    @staticmethod
    def _run_command(command: str) -> str:
        cmd = pexpect.spawn(command)
        cmd.expect(pexpect.EOF)
        cmd.kill(SIG_DFL)
        cmd.close()

        return cmd.before.decode('utf-8')

    def test_empty_start_command(self) -> None:
        """ Test the output of and empty start command. """
        output = self._run_command('tgl start')

        self.assertIn('usage: tgl start [-h] [-p] [-t [TAGS [TAGS ...]]] [-w] [-b] description', output)
        self.assertIn('tgl start: error: the following arguments are required: description', output)

    def test_start_with_one_word_description_without_quotes(self) -> None:
        """ Test the output of the timer start function with one word description. """
        output = self._run_command('tgl start description')

        self.assertIn('Timer started.', output)

    def test_start_with_one_word_description_with_quotes(self) -> None:
        """ Test the output of the timer start function with one word description. """
        output = self._run_command('tgl start "description"')

        self.assertIn('Timer started.', output)

    def test_start_with_multiword_description_without_quotes(self) -> None:
        """ Test the output of the timer start function with a multiline description not surrounded by quotes. """
        output = self._run_command('tgl start description two')

        self.assertIn('usage: tgl [-h] <commands> ...', output)
        self.assertIn('tgl: error: unrecognized arguments: two', output)


if __name__ == "__main__":
    unittest.main()
