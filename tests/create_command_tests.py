import unittest

from tgl.utils import delete_user_data
from tests.utils import setup_credentials, run_command, delete_project_with_name


class TestCreateCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        delete_user_data()
        return super().tearDown()

    def test_create_project(self) -> None:
        """ Test the output of the create project command. """
        output = run_command('tgl create project "project name for tests"')
        self.assertRegex(output, r'Project "project name for tests" has been created in the ".*" workspace.')

        delete_project_with_name('project name for tests')


if __name__ == "__main__":
    unittest.main()
