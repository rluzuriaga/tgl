import unittest

from tests.utils import run_command


class TestHelpMessages(unittest.TestCase):
    generic_help_argument_regex: str = r"-h, --help \s* show this help message and exit"

    def test_empty_tgl_command(self) -> None:
        out = run_command("tgl")
        self.assertIn("usage: tgl [-h] <commands> ...", out)

    def test_help_commands(self) -> None:
        out1 = run_command("tgl -h")
        self.assertIn("usage: tgl [-h] <commands> ...", out1)

        out2 = run_command("tgl --help")
        self.assertIn("usage: tgl [-h] <commands> ...", out2)

    def test_wrong_command(self) -> None:
        out = run_command("tgl error", error=True)
        self.assertIn("usage: tgl [-h] <commands> ...", out)
        self.assertIn("tgl: error: argument <commands>: invalid choice: 'error' (choose from", out)

    def test_setup_help_command(self) -> None:
        out = run_command("tgl setup -h")
        self.assertIn("usage: tgl setup [-h] [-a]", out)
        self.assertRegex(out, self.generic_help_argument_regex)
        self.assertIn("-a, --api   Use API key instead of username and password.", out)

    def test_reconfig_help_message(self) -> None:
        out = run_command("tgl reconfig -h")
        self.assertIn("usage: tgl reconfig [-h]", out)
        self.assertRegex(out, self.generic_help_argument_regex)

    def test_start_help_message(self) -> None:
        out = run_command("tgl start -h")
        self.assertIn("usage: tgl start [-h] [-p] [-t [TAGS [TAGS ...]]] [-w] [-b] description", out)
        self.assertRegex(out, self.generic_help_argument_regex)
        self.assertRegex(out, r"description \s* Timer description, use quotes around it unless it is\n\s* one word.")
        self.assertRegex(out, r"-p, --project \s* Start timer in select project.")
