import unittest

from tests.utils import run_command


class TestCommandsWithoutSetup(unittest.TestCase):
    def test_start_command(self) -> None:
        """ Test the output of the start command without the setup being done. """
        output = run_command('tgl start "description"')
        self.assertIn("Please run 'tgl setup' before you can run a timer.", output)

    def test_stop_command(self) -> None:
        """ Test the output of the stop command without the setup being done. """
        output = run_command('tgl stop')
        self.assertIn("Please run 'tgl setup' before you can run a timer.", output)

    def test_current_command(self) -> None:
        """ Test the output of the current command without the setup being done. """
        output = run_command('tgl current')
        self.assertIn("Please run 'tgl setup' before you can run a timer.", output)

    def test_pause_command(self) -> None:
        """ Test the output of the pause command without the setup being done. """
        output = run_command('tgl pause')
        self.assertIn("Please run 'tgl setup' before you can run a timer.", output)

    def test_resume_command(self) -> None:
        """ Test the output of the resume command without the setup being done. """
        output = run_command('tgl resume')
        self.assertIn("Please run 'tgl setup' before you can run a timer.", output)

    def test_reconfig_command(self) -> None:
        """ Test the output of the reconfig command without the setup being done. """
        output = run_command('tgl reconfig')
        self.assertIn("Please run 'tgl setup' before you can run a timer.", output)

    def test_create_project_command(self) -> None:
        """ Test the output of the create project command without the setup being done. """
        output = run_command('tgl create project project_name')
        self.assertIn("Please run 'tgl setup' before you can run a timer.", output)


if __name__ == "__main__":
    unittest.main()
