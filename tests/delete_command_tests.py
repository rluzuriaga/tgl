import unittest

from tgl.utils import delete_user_data
from tests.utils import run_command, setup_credentials


class TestDeleteCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        setup_credentials()
        return super().setUp()

    def tearDown(self) -> None:
        delete_user_data()
        return super().tearDown()

    def test_delete_project_with_none_available(self) -> None:
        """ Test the output of the delete project command without any available project. """
        output = run_command('tgl delete project')
        self.assertIn('There are no projects available in the config file.', output)
        self.assertIn(
            'If you recently added a project to your account, please use "tgl reconfig" to reconfigure your data.',
            output
        )


if __name__ == "__main__":
    unittest.main()
