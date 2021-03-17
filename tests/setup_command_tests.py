import os
import unittest

import pexpect
from dotenv import load_dotenv

from tgl.utils import delete_user_data, are_defaults_empty

load_dotenv()


class TestSetupCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        return super().setUp()

    def tearDown(self) -> None:
        delete_user_data()
        return super().tearDown()

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

    def test_bad_password(self) -> None:
        """ Test the output when the user enters an incorrect password. """
        output = self._setup_command(os.environ.get('EMAIL'), 'bad_password')

        self.assertIn('Error: Incorrect credentials.', output)

    def test_valid_credentials(self) -> None:
        """ Test the output when entering a valid email and password. """
        output = self._setup_command(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))

        self.assertIn('Data saved.', output)
        # TODO: Need to make the assert work by reloading the config file in tgl.utils
        # self.assertFalse(are_defaults_empty())

    def test_run_setup_second_time_without_reconfig(self) -> None:
        """ Test the setup command after data is already saved and make sure that the data is not overwritten. """
        output = self._setup_command(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))

        self.assertRegex(output, r'Data saved.')

        cmd = pexpect.spawn('tgl setup')

        cmd.expect(r'User data is not empty. Do you want to reconfigure it\? \(y/N\)')
        cmd.sendline('N')

        cmd.expect(pexpect.EOF)
        cmd.close()

        self.assertIn('Data was not changed.', cmd.before.decode('utf-8'))
        # TODO: Need to make the assert work by reloading the config file in tgl.utils
        # self.assertFalse(are_defaults_empty())

    def test_run_setup_second_time_with_empty_reconfig(self) -> None:
        """ Test running the setup command a second time with and empty email and password.
        Doing this should result in the original data being deleted from the the json file. 
        """
        output = self._setup_command(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))
        self.assertRegex(output, r'Data saved.')

        cmd = pexpect.spawn('tgl setup')
        cmd.expect(r'User data is not empty. Do you want to reconfigure it\? \(y/N\)')
        cmd.sendline('y')
        self.assertTrue(are_defaults_empty())

        output = self._setup_command('\n', '\n')
        self.assertIn('Nothing entered, closing program.', output)
        self.assertTrue(are_defaults_empty())


if __name__ == "__main__":
    unittest.main()
