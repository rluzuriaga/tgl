import os
import unittest
import subprocess
from signal import SIG_DFL

import pexpect
from dotenv import load_dotenv

from tgl.utils import delete_user_data

load_dotenv()


def tgl_stop() -> None:
    """ Stop any timer that is running. """
    subprocess.run(['tgl', 'stop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class TestStartCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        self._setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        tgl_stop()

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
        """ Test the output of the timer start function with a multiword description not surrounded by quotes. 
        This command output should result in an error.
        """
        output = self._run_command('tgl start description two')

        self.assertIn('usage: tgl [-h] <commands> ...', output)
        self.assertIn('tgl: error: unrecognized arguments: two', output)

    def test_start_with_multiword_description_with_quotes(self) -> None:
        """ Test the output of the timer start function with a multiword description in quotes. 
        This command output should work without any issue.
        """
        output = self._run_command('tgl start "multiword description with quotes"')

        self.assertIn('Timer started.', output)

    def test_start_with_project_argument_with_no_project_available(self) -> None:
        """ Test the output of the timer start function with the `-p` argument when there is no project available. 

        This command output should print out a warning to the user about there not being any project in the account 
            but still start a timer.
        """
        output = self._run_command('tgl start -p "This is a test timer"')

        self.assertIn("WARNING: You don't have any projects in your account.", output)
        self.assertIn("If you created one recently, please run 'tgl reconfig' to reconfigure your data.", output)
        self.assertIn("Timer will be crated without project.", output)
        self.assertIn("Timer started.", output)

    # TODO: Make test with a valid project

    def test_start_with_one_single_word_tag(self) -> None:
        """ Test that the `tgl start [-t/--tags]` commands works with a single one-word tag. """
        out1 = self._run_command('tgl start "description" -t tag1')
        self.assertIn('Timer started.', out1)
        tgl_stop()

        out2 = self._run_command('tgl start "description" --tags tag2')
        self.assertIn('Timer started.', out2)

    def test_start_with_one_multiword_tag(self) -> None:
        """ Test that the `tgl start [-t/--tags]` commands works with a single multiword tag. """
        out1 = self._run_command('tgl start "description" -t "tag 1 with spaces"')
        self.assertIn('Timer started.', out1)
        tgl_stop()

        out2 = self._run_command('tgl start "description" --tags "tag 2 with spaces"')
        self.assertIn('Timer started.', out2)

    def test_start_with_multiple_one_word_tags(self) -> None:
        """ Test that the `tgl start [-t/--tags]` commands works with a multiple one-word tags. """
        out1 = self._run_command('tgl start "description" -t tag3 tag4')
        self.assertIn('Timer started.', out1)
        tgl_stop()

        out2 = self._run_command('tgl start "description" --tags tag3 tag4')
        self.assertIn('Timer started.', out2)

    def test_start_with_multiple_multiword_tags(self) -> None:
        """ Test that the `tgl start [-t/--tags]` commands works with a multiple multiword tags. """
        out1 = self._run_command('tgl start "description" -t "tag 3 with spaces" "tag 4 with spaces"')
        self.assertIn('Timer started.', out1)
        tgl_stop()

        out2 = self._run_command('tgl start "description" --tags "tag 3 with spaces" "tag 4 with spaces"')
        self.assertIn('Timer started.', out2)


if __name__ == "__main__":
    unittest.main()
