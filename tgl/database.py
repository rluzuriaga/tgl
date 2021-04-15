import os
import sqlite3
from functools import wraps
from typing import Any, Callable, List, Tuple, Optional, Union

from tgl.config import DatabasePath


class Database:
    def __init__(self) -> None:
        # Check if the database is already created
        # If it isn't then run the function to create it
        if not os.path.exists(DatabasePath.get()):
            self._create_db()

    def _setup(self) -> None:
        self.connection = sqlite3.connect(DatabasePath.get())
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
                workspace_id TEXT PRIMARY KEY,
                workspace_name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS defaults (
                api_key TEXT NOT NULL,
                workspace_id TEXT NOT NULL,

                FOREIGN KEY (workspace_id) REFERENCES workspaces (workspace_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS projects (
                workspace_id TEXT NOT NULL,
                project_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,

                FOREIGN KEY (workspace_id) REFERENCES workspaces (workspace_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS timers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                description TEXT NOT NULL,
                project_id TEXT,
                billable INTEGER,
                tags TEXT,
                resumed INTEGER NOT NULL,

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
    def are_there_projects(self) -> bool:
        """ Check if there are any projects saved to the database.

        Returns:
            bool:   True if there are projects
                    False if there are NO projects
        """
        output = self.cursor.execute('SELECT * FROM projects').fetchall()

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
    def get_start_timer_url(self) -> str:
        """ Get the api url to start a timer.

        Returns:
            str: URL
        """
        output = self.cursor.execute(
            '''
            SELECT url
            FROM api_url
            WHERE name="start";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_current_timer_url(self) -> str:
        """ Get the api url for checking current timers that are running.

        Returns:
            str: URL
        """
        output = self.cursor.execute(
            '''
            SELECT url
            FROM api_url
            WHERE name="current";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_stop_timer_url(self) -> str:
        """ Get the api url to stop a timer.

        Returns:
            str: URL
        """
        output = self.cursor.execute(
            '''
            SELECT url
            FROM api_url
            WHERE name="stop";
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
    def get_projects_url(self) -> str:
        """ Get the api url that is used to retrieve & add projects.

        Returns:
            str: URL
        """
        output = self.cursor.execute(
            '''
            SELECT url
            FROM api_url
            WHERE name = "projects";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_list_of_workspace_ids(self) -> List[str]:
        """ Get a list of all workspace IDs.

        Returns:
            List[int]: Workspace id list.
        """
        out: List[Tuple[str, ...]] = self.cursor.execute(
            '''
            SELECT workspace_id
            FROM workspaces;
            '''
        ).fetchall()

        output: List[str] = [wid[0] for wid in out]

        return output

    @setup_and_teardown
    def get_list_of_workspace_names(self) -> List[str]:
        """ Get a list of all workspace names.

        Returns:
            List[str]: Workspace name list.
        """
        out: List[Tuple[str, ...]] = self.cursor.execute(
            '''
            SELECT workspace_name
            FROM workspaces;
            '''
        ).fetchall()

        output: List[str] = [workspace_name[0] for workspace_name in out]

        return output

    @setup_and_teardown
    def get_workspace_id_from_workspace_name(self, workspace_name: str) -> str:
        """ Get the workspace id from the workspace name.

        Args:
            workspace_name (str): Workspace name to search on the workspaces table.

        Returns:
            str: Workspace ID.
        """
        output: str = self.cursor.execute(
            f'''
            SELECT workspace_id
            FROM workspaces
            WHERE workspace_name="{workspace_name}";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_workspace_name_from_workspace_id(self, workspace_id: str) -> str:
        """ Get the workspace name from a given workspace ID.

        Args:
            workspace_id (str): The workspace ID that is searched on the database.

        Returns:
            str: Workspace Name.
        """
        output = self.cursor.execute(
            f'''
            SELECT workspace_name
            FROM workspaces
            WHERE workspace_id = "{workspace_id}";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_user_authentication(self) -> Tuple[str, str]:
        """ Get the api key from the database and return the needed authentication tuple.

        Returns:
            Tuple[str, str]: API token tuple.
        """
        out = self.cursor.execute(
            '''
            SELECT api_key
            FROM defaults;
            '''
        ).fetchall()[0][0]

        auth = (out, 'api_token')
        return auth

    @setup_and_teardown
    def get_default_workspace_id(self) -> str:
        output: str = self.cursor.execute(
            'SELECT workspace_id FROM defaults;'
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_list_of_project_names_from_workspace(self, workspace_id: str) -> List:
        out: List[Tuple[str, ...]] = self.cursor.execute(
            f'''
            SELECT project_name
            FROM projects
            WHERE workspace_id="{workspace_id}";
            '''
        ).fetchall()

        output: List[str] = [project_name[0] for project_name in out]

        return output

    @setup_and_teardown
    def get_project_id_from_project_name(self, project_name: str) -> str:
        """ Get the project ID from the given project name

        Args:
            project_name (str): User selected project name.

        Returns:
            str: Project ID.
        """
        output: str = self.cursor.execute(
            f'''
            SELECT project_id
            FROM projects
            WHERE project_name="{project_name}";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_project_name_from_project_id(self, project_id: str) -> str:
        """ Get the project name from a given project ID.

        Args:
            project_id (str): Project ID.

        Returns:
            str: The project name.
        """
        output = self.cursor.execute(
            f'''
            SELECT project_name
            FROM projects
            WHERE project_id = "{project_id}";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_workspace_name_from_project_id(self, project_id: str) -> str:
        """ Get the workspace name from a given project ID.

        Args:
            project_id (str): Project ID.

        Returns:
            str: Workspace name.
        """
        output = self.cursor.execute(
            f'''
            SELECT w.workspace_name
            FROM workspaces w
            INNER JOIN projects p
            ON w.workspace_id = p.workspace_id
            WHERE p.project_id = "{project_id}";
            '''
        ).fetchall()[0][0]

        return output

    @setup_and_teardown
    def get_projects_from_all_workspaces(self) -> List[Tuple[str, str, str]]:
        """ Get a list of tuples with the projects from all the workspaces

        Returns:
            List[Tuple[str, str, str]]: A list of tuples with the project name, workspace name, and project ID.
        """
        output = self.cursor.execute(
            '''
            SELECT DISTINCT p.project_name, w.workspace_name, p.project_id
            FROM projects p
            INNER JOIN workspaces w
            ON p.workspace_id = w.workspace_id;
            '''
        ).fetchall()

        return output

    @setup_and_teardown
    def get_paused_timer(self) -> Union[Tuple[()], Tuple[str, str, Optional[str], int, Optional[List[str]]]]:
        output = self.cursor.execute(
            '''
            SELECT workspace_id, description, project_id, billable, tags
            FROM timers
            WHERE resumed=0;
            '''
        ).fetchall()

        try:
            return output[0]
        except IndexError:
            return ()

    @setup_and_teardown
    def set_paused_timer_as_resumed(self) -> None:
        self.cursor.execute(
            '''
            UPDATE timers
            SET resumed = 1
            WHERE resumed = 0;
            '''
        )
        self.connection.commit()

    @setup_and_teardown
    def add_workspaces_data(self, workspace_id: str, workspace_name: str) -> None:
        self.cursor.execute(
            f'''
            INSERT INTO workspaces (workspace_id, workspace_name)
            VALUES ("{workspace_id}", "{workspace_name}");
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
    def add_projects_data(self, workspace_id: str, project_id: str, project_name: str) -> None:
        self.cursor.execute(
            f'''
            INSERT INTO projects (workspace_id, project_id, project_name)
            VALUES ("{workspace_id}", "{project_id}", "{project_name}");
            '''
        )
        self.connection.commit()

    @setup_and_teardown
    def add_paused_timer_data(self, workspace_id: str, description: str,
                              project_id: Optional[str], billable: bool,
                              tags: Optional[List[str]]) -> None:
        """ Generate an INSERT sql statement with the paused timer data and commit it to the database.

        Args:
            workspace_id (str): The workspace ID that the timer was running on.
            description (str): The description of the timer.
            project_id (Optional[str]): The project ID for the timer OR None if no project ID used.
            billable (bool): Boolean if the timer is billable or not
            tags (Optional[List[str]]): List of strings of the tags OR None if not tags were used.
        """

        sql_statement = f'''\
                        INSERT INTO timers (workspace_id, description, project_id, billable, tags, resumed)\
                        VALUES ("{workspace_id}", "{description}",\
                        '''

        if project_id is None:
            sql_statement += "NULL, "
        else:
            sql_statement += f'"{project_id}", '

        sql_statement += f"{int(billable)}, "

        if tags is None:
            sql_statement += "NULL, "
        else:
            sql_statement += f'"{",".join(tags)}", '

        # Set the resumed column to false.
        sql_statement += "0);"

        self.cursor.execute(sql_statement)
        self.connection.commit()
