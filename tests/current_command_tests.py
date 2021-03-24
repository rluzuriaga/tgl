import unittest

from tgl.utils import delete_user_data
from tests.utils import tgl_stop, setup_credentials, run_command


class TestCurrentCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        tgl_stop()
        delete_user_data()
        return super().tearDown()

    def test_current_with_no_running_timer(self) -> None:
        """ Test the output of the current command without any timer running. """
        output = run_command('tgl current')
        self.assertIn('There is no timer currently running.', output)

    def test_current_with_timer_running(self) -> None:
        """ Test the output of the current command with a timer running. """
        _ = run_command('tgl start "description"')

        output = run_command('tgl current')

        self.assertIn('Current timer:', output)
        self.assertRegex(output, r'Description:\s*description')
        self.assertRegex(output, r'Running time:\s*0:00:\d*')


if __name__ == "__main__":
    unittest.main()
