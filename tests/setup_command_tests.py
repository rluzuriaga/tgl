import unittest

import pexpect


class TestSetupCommand(unittest.TestCase):
    def _setup_command(self, email, password) -> str:
        cmd = pexpect.spawn('tgl setup')

        cmd.expect('Please enter your email address:')
        cmd.sendline(email)

        cmd.expect('Please enter your password:')
        cmd.sendline(password)

        cmd.expect(pexpect.EOF)
        cmd.close()

        return cmd.before.decode('utf-8')

    def test_empty_setup_config(self) -> None:
        """ Test the output when the user doesn't enter anything (presses Enter) for email and password. """
        output = self._setup_command('\n', '\n')

        self.assertIn('Nothing entered, closing program.', output)

    def test_bad_email(self) -> None:
        """ Test the output when the user enters an incorrect email. """
        output = self._setup_command('this_is_a_bad_email@bad_email.com', '\n')

        self.assertIn('Error: Incorrect credentials.', output)


if __name__ == "__main__":
    unittest.main()
