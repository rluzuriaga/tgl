import os
import sqlite3
from functools import wraps
from typing import Any, Callable, List, Tuple

from tgl.config import DatabasePath


class Database:
    def __init__(self, database_path: str = DatabasePath.get()) -> None:
        self.db_path: str = database_path

        # Check if the database is already created
        # If it isn't then run the function to create it
        if not os.path.exists(self.db_path):
            self._create_db()

    def _setup(self) -> None:
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def _teardown(self) -> None:
        self.cursor.close()
        self.connection.close()

        del self.cursor
        del self.connection

    def setup_and_teardown(func: Callable) -> Callable:  # type: ignore
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            self._setup()

            function_return = func(self, *args, **kwargs)

            self._teardown()

            return function_return
        return wrapper

    @setup_and_teardown
    def _create_db(self) -> None:
        """ Function to create the database schema and fill it with the needed data. """
        # Create table schema
        self.cursor.executescript(
            '''
            CREATE TABLE IF NOT EXISTS api_url (
                name TEXT PRIMARY KEY,
                url TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS workspaces (
                workspace_id INTEGER PRIMARY KEY,
                workspace_name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS defaults (
                api_key TEXT NOT NULL,
                workspace_id INTEGER NOT NULL,

                FOREIGN KEY (workspace_id) REFERENCES workspaces (workspace_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS projects (
                workspace_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,

                FOREIGN KEY (workspace_id) REFERENCES workspaces (workspace_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            );
            '''
        )
        self.connection.commit()

        # Insert data into the needed tables
        self.cursor.executescript(
            '''
            INSERT INTO api_url (name, url) VALUES ("user_info", "https://api.track.toggl.com/api/v8/me");
            INSERT INTO api_url (name, url) VALUES ("start", "https://api.track.toggl.com/api/v8/time_entries/start");
            INSERT INTO api_url (name, url) VALUES ("current", "https://api.track.toggl.com/api/v8/time_entries/current");
            INSERT INTO api_url (name, url) VALUES ("stop", "https://api.track.toggl.com/api/v8/time_entries/{}/stop");
            INSERT INTO api_url (name, url) VALUES ("projects", "https://api.track.toggl.com/api/v8/projects");
            INSERT INTO api_url (name, url) VALUES ("projects_from_workspace_id", "https://api.track.toggl.com/api/v8/workspaces/{}/projects");
            '''
        )
        self.connection.commit()

    @setup_and_teardown
    def is_user_data_saved(self) -> bool:
        """ Check if user data is saved to the database.
        The function checks if there is any data in the defaults table since that is te table that
            will always contain data after the user runs `tgl setup`.

        Returns:
            bool:   True if user data is saved to the database.
                    False if user data is not saved to the database.
        """
        output = self.cursor.execute('SELECT * FROM defaults;').fetchall()

        return bool(output)

    @setup_and_teardown
    def delete_user_data(self) -> None:
        """ Delete all user data from the database like if the database had just been initialized. """
        # Check how to create a savepoint in case it should be rolledback
        # https://sqlite.org/lang_savepoint.html
        self.cursor.executescript(
            '''
            DELETE FROM projects;
            DELETE FROM defaults;
            DELETE FROM workspaces;
            '''
        )
        self.connection.commit()

    @setup_and_teardown
    def get_user_info_url(self) -> str:
        """ Get the api url for checking user information.

        Returns:
            str: URL
        """
        output = self.cursor.execute(
            '''
            SELECT url
            FROM api_url
            WHERE name="user_info";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_project_from_workspace_id_url(self) -> str:
        """ Get the api url that is used retrieve the projects for a specific workspace.

        Returns:
            str: URL
        """
        output = self.cursor.execute(
            '''
            SELECT url
            FROM api_url
            WHERE name = "projects_from_workspace_id";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_list_of_workspace_id_from_workspaces(self) -> List[int]:
        out: List[Tuple[int, ...]] = self.cursor.execute(
            '''
            SELECT workspace_id
            FROM workspaces;
            '''
        ).fetchall()

        output: List[int] = [wid[0] for wid in out]

        return output

    @setup_and_teardown
    def add_workspaces_data(self, workspace_id: int, workspace_name: str) -> None:
        self.cursor.execute(
            f'''
            INSERT INTO workspaces (workspace_id, workspace_name)
            VALUES ({workspace_id}, "{workspace_name}");
            '''
        )
        self.connection.commit()

    @setup_and_teardown
    def add_defaults_data(self, api_key: str, workspace_id: int) -> None:
        self.cursor.execute(
            f'''
            INSERT INTO defaults (api_key, workspace_id)
            VALUES ("{api_key}", {workspace_id});
            '''
        )
        self.connection.commit()

    @setup_and_teardown
    def add_projects_data(self, workspace_id: int, project_id: int, project_name: str) -> None:
        self.cursor.execute(
            f'''
            INSERT INTO projects (workspace_id, project_id, project_name)
            VALUES ({workspace_id}, {project_id}, "{project_name}");
            '''
        )
        self.connection.commit()
