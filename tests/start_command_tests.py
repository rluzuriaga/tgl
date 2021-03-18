import unittest
from signal import SIG_DFL

import pexpect

from tgl.utils import delete_user_data


class TestStartCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        return super().setUp()

    def tearDown(self) -> None:
        delete_user_data()
        return super().tearDown()

    def test_empty_start_command(self) -> None:
        """ Test the output of and empty start command. """
        cmd = pexpect.spawn('tgl start')
        cmd.expect(pexpect.EOF)
        cmd.kill(SIG_DFL)
        cmd.close()

        output = cmd.before.decode('utf-8')

        self.assertIn('usage: tgl start [-h] [-p] [-t [TAGS [TAGS ...]]] [-w] [-b] description', output)
        self.assertIn('tgl start: error: the following arguments are required: description', output)


if __name__ == "__main__":
    unittest.main()
