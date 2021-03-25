import unittest

from tgl.utils import delete_user_data
from tests.utils import setup_credentials, run_command, tgl_stop


class TestPauseCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        tgl_stop()
        delete_user_data()
        return super().tearDown()

    def test_pause_without_any_timer_running(self) -> None:
        """ Test the output of pause command with no timer running. """
        output = run_command('tgl pause')
        self.assertIn('There is no timer currently running.', output)

    def test_pause_with_timer_running(self) -> None:
        """ Test the output of the pause command with a timer running. """
        _ = run_command('tgl start "description for pause"')

        output = run_command('tgl pause')
        self.assertIn('Timer "description for pause" paused.', output)
        self.assertIn('Resume using "tgl resume".', output)


if __name__ == "__main__":
    unittest.main()
