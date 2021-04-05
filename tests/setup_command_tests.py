import os
import unittest
from time import sleep
from signal import SIG_DFL

import pexpect
from dotenv import load_dotenv

from tgl.config import DatabasePath
from tgl.database import Database
from tests.utils import remove_db_file

load_dotenv()

DATABASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'setup_tests_db.sqlite3')


class TestSetupCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        DatabasePath.set(DATABASE_PATH)
        return super().setUpClass()

    def setUp(self) -> None:
        remove_db_file()
        return super().setUp()

    def tearDown(self) -> None:
        remove_db_file()
        return super().tearDown()

    def _setup_command(self, email, password) -> str:
        cmd = pexpect.spawn(f'tgl -d {DATABASE_PATH} setup')

        cmd.expect('Please enter your email address:')
        cmd.sendline(email)

        cmd.expect('Please enter your password:')
        cmd.sendline(password)

        cmd.expect(pexpect.EOF)
        cmd.kill(SIG_DFL)
        cmd.close()

        return cmd.before.decode('utf-8')

    def test_empty_setup_config(self) -> None:
        """ Test the output when the user doesn't enter anything (presses Enter) for email and password. """
        output = self._setup_command('\n', '\n')

        self.assertIn('Nothing entered, closing program.', output)
        self.assertFalse(Database().is_user_data_saved())

    def test_empty_api_setup_config(self) -> None:
        """ Test the output when the user doesn't enter anything (presses Enter) for the api. """
        cmd = pexpect.spawn(f'tgl -d {DATABASE_PATH} setup -a')

        cmd.expect("Please enter your API token \(found under 'Profile settings' in the Toggl website\):")
        cmd.sendline('\n')

        cmd.expect(pexpect.EOF)
        cmd.kill(SIG_DFL)
        cmd.close()

        self.assertIn('Nothing entered, closing program.', cmd.before.decode('utf-8'))
        self.assertFalse(Database().is_user_data_saved())

    def test_bad_email(self) -> None:
        """ Test the output when the user enters an incorrect email. """
        output = self._setup_command('this_is_a_bad_email@bad_email.com', '\n')

        self.assertIn('Error: Incorrect credentials.', output)
        self.assertFalse(Database().is_user_data_saved())

    def test_bad_password(self) -> None:
        """ Test the output when the user enters an incorrect password. """
        output = self._setup_command(os.environ.get('EMAIL'), 'bad_password')

        self.assertIn('Error: Incorrect credentials.', output)
        self.assertFalse(Database().is_user_data_saved())

    def test_valid_email_and_password_credentials(self) -> None:
        """ Test the output when entering a valid email and password. """
        output = self._setup_command(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))

        self.assertIn('Data saved.', output)
        self.assertTrue(Database().is_user_data_saved())

    def test_valid_api_credentials(self) -> None:
        cmd = pexpect.spawn(f'tgl -d {DATABASE_PATH} setup -a')

        cmd.expect("Please enter your API token \(found under 'Profile settings' in the Toggl website\):")
        cmd.sendline(os.environ.get('API_KEY'))

        cmd.expect(pexpect.EOF)
        cmd.kill(SIG_DFL)
        cmd.close()

        self.assertIn('Data saved.', cmd.before.decode('utf-8'))
        self.assertTrue(Database().is_user_data_saved())

    def test_run_setup_second_time_without_reconfig(self) -> None:
        """ Test the setup command after data is already saved and make sure that the data is not overwritten. """
        output = self._setup_command(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))

        self.assertRegex(output, r'Data saved.')
        self.assertTrue(Database().is_user_data_saved())

        cmd = pexpect.spawn(f'tgl -d {DATABASE_PATH} setup')

        cmd.expect(r'User data is not empty. Do you want to reconfigure it\? \(y/N\)')
        cmd.sendline('N')

        cmd.expect(pexpect.EOF)
        cmd.close()

        self.assertIn('Data was not changed.', cmd.before.decode('utf-8'))
        self.assertTrue(Database().is_user_data_saved())

    def test_run_setup_second_time_with_empty_reconfig(self) -> None:
        """ Test running the setup command a second time with and empty email and password.
        Doing this should result in the original data being deleted from the the json file. 
        """
        # First setup command with correct email and password
        output = self._setup_command(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))
        self.assertRegex(output, r'Data saved.')
        self.assertTrue(Database().is_user_data_saved())

        # Second setup command with `y` reconfigure and empty email and password
        cmd = pexpect.spawn(f'tgl -d {DATABASE_PATH} setup')
        cmd.expect(r'User data is not empty. Do you want to reconfigure it\? \(y/N\)')
        cmd.sendline('y')

        # The user data in the database should be removed right after the user enters `y`
        # Need to wait a tiny bit for the data to be removed from the database before checking it.
        sleep(0.001)
        self.assertFalse(Database().is_user_data_saved())

        # Entering nothing for email and password
        cmd.expect('Please enter your email address:')
        cmd.sendline('\n')

        cmd.expect('Please enter your password:')
        cmd.sendline('\n')

        cmd.expect(pexpect.EOF)
        cmd.close()

        self.assertIn('Nothing entered, closing program.', cmd.before.decode('utf-8'))
        self.assertFalse(Database().is_user_data_saved())

    def test_run_setup_second_time_with_credentials(self) -> None:
        """ Test running the setup command a second time with a different email and password.
        Doing this should result in the original data being removed and new data going in its place.
        """
        # First setup command with correct email and password
        output = self._setup_command(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))
        self.assertRegex(output, r'Data saved.')
        self.assertTrue(Database().is_user_data_saved())

        # Second setup command with `y` reconfigure and valid credentials
        cmd = pexpect.spawn(f'tgl -d {DATABASE_PATH} setup')
        cmd.expect(r'User data is not empty. Do you want to reconfigure it\? \(y/N\)')
        cmd.sendline('y')

        # The user data in the database should be removed right after the user enters `y`
        # Need to wait a tiny bit for the data to be removed from the database before checking it.
        sleep(0.001)
        self.assertFalse(Database().is_user_data_saved())

        cmd.expect('Please enter your email address:')
        cmd.sendline(os.environ.get('EMAIL'))

        cmd.expect('Please enter your password:')
        cmd.sendline(os.environ.get('PASSWORD'))

        cmd.expect(pexpect.EOF)
        cmd.close()

        self.assertIn('Data saved.', cmd.before.decode('utf-8'))
        self.assertTrue(Database().is_user_data_saved())


if __name__ == "__main__":
    unittest.main()
