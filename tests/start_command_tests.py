import unittest

from tgl.utils import delete_user_data


class TestStartCommand(unittest.TestCase):
    def setUp(self) -> None:
        delete_user_data()
        return super().setUp()

    def tearDown(self) -> None:
        delete_user_data()
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
