import os


class DatabasePath:
    path: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db.sqlite3')

    @classmethod
    def get(cls) -> str:
        return cls.path

    @classmethod
    def set(cls, new_path: str) -> None:
        cls.path = new_path
