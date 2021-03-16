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


if __name__ == "__main__":
    unittest.main()
