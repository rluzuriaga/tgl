import unittest
import subprocess


def run_command(cmd: str, error: bool = False) -> str:
    output = subprocess.run(cmd.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    output_string = output.stdout.decode('utf-8')

    if error:
        output_string = output.stderr.decode('utf-8')

    return output_string


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
        out1 = run_command("tgl setup -h")
        self.assertIn("usage: tgl setup [-h] [-a]", out1)
        self.assertRegex(out1, self.generic_help_argument_regex)
        self.assertIn("-a, --api   Use API key instead of username and password.", out1)

        out2 = run_command("tgl setup --help")
        self.assertIn("usage: tgl setup [-h] [-a]", out2)
        self.assertRegex(out2, self.generic_help_argument_regex)
        self.assertIn("-a, --api   Use API key instead of username and password.", out2)

    def test_reconfig_help_message(self) -> None:
        out1 = run_command("tgl reconfig -h")
        self.assertIn("usage: tgl reconfig [-h]", out1)
        self.assertRegex(out1, self.generic_help_argument_regex)

        out2 = run_command("tgl reconfig --help")
        self.assertIn("usage: tgl reconfig [-h]", out2)
        self.assertRegex(out2, self.generic_help_argument_regex)

    def test_start_help_message(self) -> None:
        out1 = run_command("tgl start -h")
        self.assertIn("usage: tgl start [-h] [-p] [-t [TAGS [TAGS ...]]] [-w] [-b] description", out1)
        self.assertRegex(out1, self.generic_help_argument_regex)
        self.assertRegex(out1, r"description \s* Timer description, use quotes around it unless it is\n\s* one word.")
        self.assertRegex(out1, r"-p, --project \s* Start timer in select project.")
        self.assertRegex(out1, r"-t \[TAGS \[TAGS ...]],\s* --tags .*\s* Space seperated .*\s* multiple .*\s* quotes.")
        self.assertRegex(out1, r"-w, --workspace \s* Select workspace to use for timer.")
        self.assertRegex(out1, r"-b, --billable \s* Set as billable hours. \(For Toggl Pro members only\).")

        out2 = run_command("tgl start --help")
        self.assertIn("usage: tgl start [-h] [-p] [-t [TAGS [TAGS ...]]] [-w] [-b] description", out2)
        self.assertRegex(out2, self.generic_help_argument_regex)
        self.assertRegex(out2, r"description \s* Timer description, use quotes around it unless it is\n\s* one word.")
        self.assertRegex(out2, r"-p, --project \s* Start timer in select project.")
        self.assertRegex(out2, r"-t \[TAGS \[TAGS ...]],\s* --tags .*\s* Space seperated .*\s* multiple .*\s* quotes.")
        self.assertRegex(out2, r"-w, --workspace \s* Select workspace to use for timer.")
        self.assertRegex(out2, r"-b, --billable \s* Set as billable hours. \(For Toggl Pro members only\).")

    def test_current_help_message(self) -> None:
        out1 = run_command("tgl current -h")
        self.assertIn("usage: tgl current [-h]", out1)
        self.assertRegex(out1, self.generic_help_argument_regex)

        out2 = run_command("tgl current --help")
        self.assertIn("usage: tgl current [-h]", out2)
        self.assertRegex(out2, self.generic_help_argument_regex)

    def test_stop_help_message(self) -> None:
        out1 = run_command("tgl stop -h")
        self.assertIn("usage: tgl stop [-h]", out1)
        self.assertRegex(out1, self.generic_help_argument_regex)

        out2 = run_command("tgl stop --help")
        self.assertIn("usage: tgl stop [-h]", out2)
        self.assertRegex(out2, self.generic_help_argument_regex)

    def test_pause_help_message(self) -> None:
        out1 = run_command("tgl pause -h")
        self.assertIn("usage: tgl pause [-h]", out1)
        self.assertRegex(out1, self.generic_help_argument_regex)

        out2 = run_command("tgl pause --help")
        self.assertIn("usage: tgl pause [-h]", out2)
        self.assertRegex(out2, self.generic_help_argument_regex)

    def test_resume_help_message(self) -> None:
        out1 = run_command("tgl resume -h")
        self.assertIn("usage: tgl resume [-h]", out1)
        self.assertRegex(out1, self.generic_help_argument_regex)

        out2 = run_command("tgl resume --help")
        self.assertIn("usage: tgl resume [-h]", out2)
        self.assertRegex(out2, self.generic_help_argument_regex)

    def test_create_help_message(self) -> None:
        out1 = run_command("tgl create -h")
        self.assertIn("usage: tgl create [-h] {project} name", out1)
        self.assertRegex(out1, r"\{project\} \s* Create a new project.")
        self.assertRegex(out1, r"name \s* Name for the project.")
        self.assertRegex(out1, self.generic_help_argument_regex)

        out2 = run_command("tgl create --help")
        self.assertIn("usage: tgl create [-h] {project} name", out2)
        self.assertRegex(out2, r"\{project\} \s* Create a new project.")
        self.assertRegex(out2, r"name \s* Name for the project.")
        self.assertRegex(out2, self.generic_help_argument_regex)


if __name__ == "__main__":
    unittest.main()
