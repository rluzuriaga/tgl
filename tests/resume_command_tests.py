import unittest

from tgl.utils import delete_user_data
from tests.utils import setup_credentials, run_command, tgl_stop


class TestResumeCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        tgl_stop()
        delete_user_data()
        return super().tearDown()

    def test_resume_without_a_paused_timer(self) -> None:
        """ Test the output of the resume command without any paused timer. """
        output = run_command('tgl resume')
        self.assertIn('There is no paused timer. Use "tgl start" to start a new timer.', output)

    def test_resume_with_paused_timer(self) -> None:
        """ Test the output of the resume command with a paused timer. """
        _ = run_command('tgl start "description"')

        _ = run_command('tgl pause')

        output = run_command('tgl resume')
        self.assertIn('Timer "description" resumed.', output)


if __name__ == "__main__":
    unittest.main()
