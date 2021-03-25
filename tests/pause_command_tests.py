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


if __name__ == "__main__":
    unittest.main()
