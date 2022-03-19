# Standard Library
import json
import re
import os
import shutil
from datetime import datetime
from sqlite3 import Error, connect, ProgrammingError

# External Libraries
import PySimpleGUI as sg
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
import pyperclip

# Internal modules
from .utilities.utilities import get_newest_file, range_parser
from .utilities.arguments import parse_args

# Version
from .utilities.version import __version__


class SJournal:
    def __init__(self, args):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.user_home_dir = os.path.expanduser('~')
        self.config_file = os.path.join(self.user_home_dir, "sjournal", "sjournal_config.json")
        self.db_file = ""
        self.journal_dir = ""
        self.journal_name = ""
        self.args = args
        self.console = Console()
        self.load()

        # self.create_connection()
        self.table = Table(title=self.journal_name)
        self.setup_table()

    def setup_table(self):
        self.table.add_column("ID", style="cyan")
        self.table.add_column("Timestamp")
        self.table.add_column("Category", style="bold green")
        self.table.add_column("Content", style="white")

    def handle_args(self):
        # If a command was specified, use it. Otherwise, assume List command
        # If command is "load", it is already run at startup, so don't run it again

        if self.args.command:
            if self.args.command != "load":
                return getattr(self, self.args.command)
        else:
            return self.list

    def create_connection(self):
        try:
            conn = connect(self.db_file)
            self.connection = conn
        except Error:
            self.console.print(Error)
            self.connection = None

    def close_connection(self):
        self.connection.close()

    def new_cursor(self):
        try:
            return self.connection.cursor()
        except ProgrammingError:
            self.create_connection()
            return self.connection.cursor()

    def run(self):

        self.create_connection()

        if not self.table_exists("notes"):
            self.create_table("notes", "id integer PRIMARY KEY, timestamp text, category text, content text")

        action = self.handle_args()

        if self.args.debug:
            self.console.print(self.args)
            debug_file = os.path.join(self.user_home_dir, "sjournal", "reports", "debug.log")

            # Make the reports directory in ~/sjournal/ if it does not exist
            if not os.path.isdir(os.path.dirname(debug_file)):
                os.makedirs(os.path.dirname(debug_file))
            self.console.print(f"debug output at {debug_file}")

            with open(debug_file, "wt") as debug_log:
                self.console = Console(file=debug_log, width=100)
                if action:
                    action()
        else:
            if action:
                action()

        self.close_connection()

    def table_exists(self, table_name):
        cursor = self.new_cursor()
        cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        # if the count is 1, then table exists
        if cursor.fetchone()[0] == 1:
            return True
        else:
            return False

    def create_table(self, name, table_string):
        query = f"CREATE TABLE {name}({table_string})"
        cursor = self.new_cursor()
        cursor.execute(query)
        self.connection.commit()

    def insert_into_database_table(self, table_name, note):
        cursor = self.new_cursor()
        cursor.execute(f"INSERT INTO {table_name} (id, timestamp, category, content) VALUES (:id, :timestamp, :category, :content)", note.dict)
        self.connection.commit()

    def add_gui(self):
        sg.theme('DarkGrey')

        layout = [
            [sg.Text(f"Add note to table \"{self.table.title}\" at {self.db_file}")],
            [
              sg.Text('{:10}'.format('Category:')),
              sg.InputText(key="category",
                           default_text="General",
                           size=(25, 1))
            ],
            [
              sg.Text('{:10}'.format('Style:')), sg.InputText(key="style", size=(25, 1))
            ],
            [
              sg.Text('{:10}'.format('Content:')), sg.InputText(key="content", size=(50, 1))
            ],
            [
              sg.Button('Save Note'), sg.Button('Cancel')
            ]
        ]

        window = sg.Window('Window Title', layout, font='Courier')

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel':
                break
            elif event == "Save Note":
                break
        window.close()

        if event == "Save Note":
            return values
        else:
            return None

    def add(self):
        cursor = self.new_cursor()

        if len(self.args.content) == 0:
            values = self.add_gui()
            if values:
                self.args.style = values['style']
                self.args.category = values['category']
                self.args.content = [values['content']]
            else:
                exit()
        note_content = ' '.join(self.args.content)
        if self.args.style:
            note_content = f"[{self.args.style}]{note_content}[/]"
        else:
            note_content = note_content

        note_data = {"category": self.args.category, "content": note_content}

        cursor.execute(f"SELECT id FROM notes ORDER BY id DESC LIMIT 1")

        try:
            most_recent_id = cursor.fetchone()[0]
        except TypeError:
            most_recent_id = -1

        note = Note(most_recent_id+1, note_data["category"], note_data["content"])
        self.insert_into_database_table("notes", note)
        self.connection.commit()

    def insert_into_print_table(self, note):
        self.table.add_row(str(note.id), str(note.timestamp), str(note.category), note.content)

    def show_print_table(self):
        self.console.print(self.table)

    def edit(self):

        cursor = self.new_cursor()

        if self.args.id is not None:
            id_to_edit = self.args.id
        else:
            cursor.execute(f"SELECT id FROM notes ORDER BY id DESC LIMIT 1")
            id_to_edit = cursor.fetchone()[0]

        cursor.execute(f"SELECT category, content, timestamp FROM notes WHERE id={id_to_edit} ORDER BY id DESC LIMIT 1")
        old_category, old_content, old_timestamp = cursor.fetchone()

        try:
            pyperclip.copy(old_content)
            msg = "(copied to clipboard)"
        except pyperclip.PyperclipException:
            msg = "(copy manually)"
        self.console.print(f'Editing Note #{id_to_edit} [bold cyan]{msg}[/]: "{old_content}"')

        new_content = Prompt.ask("Enter new note text", default=old_content)

        new_note = Note(id_to_edit, old_category, new_content)
        new_note.timestamp = old_timestamp
        cursor.execute(f'DELETE FROM notes WHERE id={id_to_edit}')
        self.insert_into_database_table("notes", new_note)
        self.connection.commit()

    def list(self):
        cursor = self.new_cursor()

        query = "SELECT * FROM notes"
        if hasattr(self.args, 'category') and self.args.category is not None:
            query += f" WHERE category='{self.args.category}'"
        query += " ORDER BY id DESC"

        if hasattr(self.args, "quantity") and not self.args.all:
            try:
                query += f" LIMIT {self.args.quantity[0]}"
            except TypeError:
                query += f" LIMIT {self.args.quantity}"
        elif not hasattr(self.args, "all"):
            query += f" LIMIT 5"

        cursor.execute(query)
        items_to_show = cursor.fetchall()
        if hasattr(self.args, "reverse") and self.args.reverse:
            items_to_show = items_to_show[::-1]
        for item in items_to_show:
            note = Note(item[0], item[2], item[3], date_time=datetime.strptime(item[1], "%m-%d-%y %H:%M:%S"))
            self.insert_into_print_table(note)

        self.show_print_table()

    def categories(self):
        if hasattr(self.args, 'search') and self.args.search:
            regex = f"{self.args.search}"
        else:
            regex = ".*"

        cursor = self.new_cursor()
        query = f"Select distinct category from notes ORDER BY category ASC"

        if hasattr(self.args, "quantity") and not self.args.all:
            query += f" LIMIT {self.args.quantity}"

        cursor.execute(query)
        for item in cursor.fetchall():
            match = re.search(regex.lower(), item[0].lower())
            if match:
                self.console.print(item[0])

    def delete(self):
        ids_to_delete = range_parser(self.args.delete_criteria)
        cursor = self.new_cursor()
        for id in ids_to_delete:
            if isinstance(id, int):

                cursor.execute(f'DELETE FROM notes WHERE id={id}')
                self.console.print(f"DELETED NOTE #{id}")
            else:
                regex_below = r"\W(\d*)"
                regex_above = r"(\d*)\W"
                match_below = re.search(regex_below, id)
                match_above = re.search(regex_above, id)

                if match_below and match_below.group(1).isnumeric():

                    for i in range(0, int(match_below.group(1))+1):
                        cursor.execute(f'DELETE FROM notes WHERE id={i}')
                        self.console.print(f"DELETED NOTE #{i}")

                elif match_above and match_above.group(1).isnumeric():
                    cursor.execute('SELECT max(id) FROM notes')
                    max_id = cursor.fetchone()[0]

                    for i in range(int(match_above.group(1)), max_id+1):
                        cursor.execute(f'DELETE FROM notes WHERE id={i}')
                        self.console.print(f"DELETED NOTE #{i}")

        self.connection.commit()

    def erase(self):
        cursor = self.new_cursor()
        cursor.execute('DELETE FROM notes')
        self.connection.commit()

    def search(self):
        if hasattr(self.args, 'search_criteria'):
            regex = f"{self.args.search_criteria[0]}"
        else:
            regex = ".*"

        cursor = self.new_cursor()
        query = "SELECT * FROM notes"
        if hasattr(self.args, 'category') and self.args.category is not None:
            query += f" WHERE category='{self.args.category}'"
        query += " ORDER BY id DESC"

        if hasattr(self.args, "quantity") and not self.args.all:
            query += f" LIMIT {self.args.quantity}"

        cursor.execute(query)
        for item in cursor.fetchall():
            id = item[0]
            category = item[2]
            content = item[3]
            match = re.search(regex.lower(), content.lower())
            if match:
                note = Note(id, category, content, date_time=datetime.strptime(item[1], "%m-%d-%y %H:%M:%S"))
                self.insert_into_print_table(note)

        self.show_print_table()

    def backup(self):
        backup_dir = os.path.join(self.journal_dir, "backups", self.journal_name)

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        if self.args.filename is None:
            timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
            new_filename = os.path.join(backup_dir, f"backup_{self.journal_name}_{timestamp}.db")
        else:
            new_filename = os.path.join(backup_dir, self.args.filename)

        new_filename = new_filename.replace(".db", "") + ".db"
        self.console.print(f"BACKING UP {self.db_file} TO FILE {new_filename}")
        shutil.copy(self.db_file, new_filename)

    def restore(self):
        backup_dir = os.path.join(self.journal_dir, "backups", self.journal_name)

        if self.args.filename is None:
            filename = get_newest_file(backup_dir)
        else:
            filename = os.path.join(backup_dir, self.args.filename)

        if filename and os.path.exists(filename.replace(".db", "") + ".db"):
            filename = filename.replace(".db", "") + ".db"
            self.console.print(f"RESTORING BACKUP FROM {filename}. REPLACING {self.db_file}")
            shutil.copy(filename, self.db_file)
            # self.db_file = filename
        else:
            self.console.print(f"Failed to restore backup: file not found.")

    def load(self):

        # Create sjournal directory in user home directory if it does not exist
        sjournal_dir = os.path.join(self.user_home_dir, "sjournal")
        if not os.path.isdir(sjournal_dir):
            os.makedirs(sjournal_dir)

        # Create default config file if it does not exist
        if not os.path.isfile(self.config_file):
            self.console.print(f"No config file found. Creating new one at {self.config_file}")

            config = {
                "journal_dir": os.path.join(self.user_home_dir, "sjournal", "journals"),
                "journal_name": "notes"
            }

            confstring = json.dumps(config)
            with open(self.config_file, "w") as config_file:
                config_file.write(confstring)

        # Modify the config file to use the specified journal name if given
        if hasattr(self.args, 'journal_name'):
            with open(self.config_file, "r") as config_file:
                config = json.load(config_file)

            config["journal_name"] = self.args.journal_name
            confstring = json.dumps(config)
            with open(self.config_file, "w") as config_file:
                config_file.write(confstring)

            msg = f'Set journal to {os.path.join(config["journal_dir"], config["journal_name"])}.db'
            self.console.print(msg)

            # Load the new config
            with open(self.config_file, "r") as config_file:
                config = json.load(config_file)

        # If journal name is not given, use the file specified in the config file
        else:
            with open(self.config_file, "r") as config_file:
                config = json.load(config_file)

        # If the journal directory does not exist, create it
        if not os.path.exists(os.path.join(config["journal_dir"])):
            os.makedirs(os.path.join(config["journal_dir"]))

        # Set the db_file, journal_dir, and journal_name attributes for the journal object
        self.db_file = os.path.join(config["journal_dir"], f"{config['journal_name']}.db")
        self.journal_dir = config["journal_dir"]
        self.journal_name = config["journal_name"]

    @property
    def notes(self):
        return self._get_notes()

    @property
    def length(self):
        return self._get_length()

    def _get_length(self):
        return len(self.notes)

    def _get_notes(self):
        query = "SELECT * FROM notes"
        cursor = self.new_cursor()
        cursor.execute(query)
        items = cursor.fetchall()
        notes = []
        for item in items:
            notes.append(Note(item[0], item[2], item[3], date_time=datetime.strptime(item[1], "%m-%d-%y %H:%M:%S")))
        self.close_connection()

        return notes


class Note:
    def __init__(self, id, category, content, date_time=None):
        self.id = id
        self.category = category
        self.content = content
        if not date_time:
            self.date_time = datetime.now()
        else:
            self.date_time = date_time
        self.timestamp = datetime.strftime(self.date_time, "%m-%d-%y %H:%M:%S")

    @property
    def dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "content": self.content,
            "timestamp": self.timestamp
        }

    @property
    def values(self):
        return [self.id, self.timestamp, self.category, self.content]

    def __str__(self):
        return f"[{self.id}] [{datetime.strftime(self.date_time, '%m-%d-%Y %H:%M:%S')}] [{self.category}] - {self.content}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.id == other.id and \
               self.category == other.category and \
               self.content == other.content and \
               self.timestamp == other.timestamp


def main():
    args = parse_args()

    if args.version:
        print(f"sjournal v{__version__} (Made by Sam Stuver)")

    else:
        journal = SJournal(args)
        journal.run()