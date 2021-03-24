import unittest

from tgl.utils import delete_user_data
from tests.utils import setup_credentials, run_command


class TestStopCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        delete_user_data()
        return super().tearDown()

    def test_stop_command_without_any_timer_running(self) -> None:
        """ Test the output of the stop command without any timer running. """
        output = run_command('tgl stop')

        self.assertIn('There is no timer currently running.', output)

    def test_stop_command_with_timer_running(self) -> None:
        """ Test the output of the stop command with a timer running. """
        _ = run_command('tgl start "start description"')

        output = run_command('tgl stop')
        self.assertIn('Timer "start description" stopped.', output)


if __name__ == "__main__":
    unittest.main()
