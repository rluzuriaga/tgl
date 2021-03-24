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


if __name__ == "__main__":
    unittest.main()
