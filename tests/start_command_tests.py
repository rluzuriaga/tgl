import unittest
from signal import SIG_DFL

import pexpect
from dotenv import load_dotenv

from tgl.utils import delete_user_data
from tests.utils import tgl_stop, setup_credentials

load_dotenv()


class TestStartCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        tgl_stop()

        delete_user_data()
        return super().tearDown()

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
        out1 = self._run_command('tgl start "This is a test timer" -p')

        self.assertIn("WARNING: You don't have any projects in your account.", out1)
        self.assertIn("If you created one recently, please run 'tgl reconfig' to reconfigure your data.", out1)
        self.assertIn("Timer will be crated without project.", out1)
        self.assertIn("Timer started.", out1)

        tgl_stop()

        out2 = self._run_command('tgl start "This is a test timer" --project')

        self.assertIn("WARNING: You don't have any projects in your account.", out2)
        self.assertIn("If you created one recently, please run 'tgl reconfig' to reconfigure your data.", out2)
        self.assertIn("Timer will be crated without project.", out2)
        self.assertIn("Timer started.", out2)

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

    def test_start_with_workspace_argument_with_no_other_workspace_available(self) -> None:
        """ Test the output of the timer start function with the `-w/--workspace` argument when there is no extra workspace available. 

        This command output should print out a warning to the user about there only being one workspace on the account.
        """
        out1 = self._run_command('tgl start "description" -w')
        self.assertIn("Only one workspace available in the config file.", out1)
        self.assertIn(
            "If you recently added a workspace on your account, please use 'tgl reconfig' to reconfigure your data.",
            out1)
        self.assertIn("Using default workspace.", out1)
        self.assertIn("Timer started.", out1)

        tgl_stop()

        out2 = self._run_command('tgl start "description" --workspace')
        self.assertIn("Only one workspace available in the config file.", out2)
        self.assertIn(
            "If you recently added a workspace on your account, please use 'tgl reconfig' to reconfigure your data.",
            out2)
        self.assertIn("Using default workspace.", out2)
        self.assertIn("Timer started.", out2)

    # TODO: Make test for a valid extra workspace


if __name__ == "__main__":
    unittest.main()
