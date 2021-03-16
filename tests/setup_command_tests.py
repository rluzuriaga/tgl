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
        """ Simulate the user pressing enter for both email and password instead of entering the needed data. """
        output = self._setup_command('\n', '\n')

        self.assertIn('Nothing entered, closing program.', output)


if __name__ == "__main__":
    unittest.main()
