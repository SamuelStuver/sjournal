import argparse
from datetime import datetime
import sqlite3
from sqlite3 import Error
import re
import os
import shutil
from rich.table import Table
from rich.console import Console


class ScratchPad:
    def __init__(self, db_file, args):
        self.db_file = db_file
        self.args = args
        self.create_connection()
        self.console = Console()
        self.table = Table(title="Notes")
        self.setup_table()

    def setup_table(self):
        self.table.add_column("ID", style="cyan")
        self.table.add_column("Timestamp")
        self.table.add_column("Category", style="bold green")
        self.table.add_column("Content", style="white")


    def handle_args(self):
        # If a command was specified, use it. Otherwise, assume List command
        if self.args.command:
            return getattr(self, self.args.command)
        else:
            return self.list

    def create_connection(self):
        try:
            conn = sqlite3.connect(self.db_file)
            self.connection = conn
        except Error:
            print(Error)
            self.connection = None

    def close_connection(self):
        self.connection.close()

    def run(self):
        self.setup()
        action = self.handle_args()
        if action:
            action()
        self.close_connection()

    def setup(self):
        if not self.table_exists("notes"):
            self.create_table("notes", "id integer PRIMARY KEY, timestamp text, category text, content text")

        return self

    def table_exists(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        # if the count is 1, then table exists
        if cursor.fetchone()[0] == 1:
            return True
        else:
            return False

    def create_table(self, name, table_string):
        cursor = self.connection.cursor()
        query = f"CREATE TABLE {name}({table_string})"
        cursor.execute(query)
        self.connection.commit()

    def insert_into_database_table(self, table_name, note):
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO {table_name} (id, timestamp, category, content) VALUES (:id, :timestamp, :category, :content)", note.dict)
        self.connection.commit()

    def add(self):
        note_data = {"category": self.args.category, "content": ' '.join(self.args.content)}
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT id FROM notes ORDER BY id DESC LIMIT 1")
        try:
            most_recent_id = cursor.fetchone()[0]
        except TypeError:
            most_recent_id = 0
        note = Note(most_recent_id+1, note_data["category"], note_data["content"])
        self.insert_into_database_table("notes", note)
        self.connection.commit()

    def insert_into_print_table(self, note):
        self.table.add_row(str(note.id), str(note.timestamp), str(note.category), str(note.content))

    def show_print_table(self):
        self.console.print(self.table)

    def list(self):
        cursor = self.connection.cursor()

        query = "SELECT * FROM notes"
        if hasattr(self.args, 'category') and self.args.category is not None:
            query += f" WHERE category='{self.args.category}'"
        query += " ORDER BY id DESC"

        if hasattr(self.args, "quantity") and not self.args.all:
            query += f" LIMIT {self.args.quantity}"

        cursor.execute(query)
        for item in cursor.fetchall():
            note = Note(item[0], item[2], item[3], date_time=datetime.strptime(item[1], "%m-%d-%y %H:%M:%S"))
            self.insert_into_print_table(note)
            # print(note)
        self.show_print_table()

    def delete(self):
        ids_to_delete = range_parser(self.args.delete_criteria)
        print(ids_to_delete)
        cursor = self.connection.cursor()
        for id in ids_to_delete:
            print(id)
            if isinstance(id, int):
                print(f"DELETING NOTE #{id}")
                cursor.execute(f'DELETE FROM notes WHERE id={id}')
            else:
                regex_below = r"\W(\d*)"
                regex_above = r"(\d*)\W"
                match_below = re.search(regex_below, id)
                match_above = re.search(regex_above, id)

                if match_below and match_below.group(1).isnumeric():
                    for i in range(0, int(match_below.group(1))+1):
                        print(f"DELETING NOTE #{i}")
                        cursor.execute(f'DELETE FROM notes WHERE id={i}')
                elif match_above and match_above.group(1).isnumeric():
                    cursor.execute('SELECT max(id) FROM notes')
                    max_id = cursor.fetchone()[0]
                    for i in range(int(match_above.group(1)), max_id+1):
                        print(f"DELETING NOTE #{i}")
                        cursor.execute(f'DELETE FROM notes WHERE id={i}')
        self.connection.commit()

    def erase(self):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM notes')
        self.connection.commit()

    def search(self):

        if hasattr(self.args, 'search_criteria'):
            regex = f".*{self.args.search_criteria[0]}.*"
        else:
            regex = ".*"

        cursor = self.connection.cursor()
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
                # print(note)
        self.show_print_table()

    def fetch(self):
        notes = []
        cursor = self.connection.cursor()
        query = "SELECT * FROM notes ORDER BY id DESC"
        cursor.execute(query)

        for item in cursor.fetchall():
            note = Note(item[0], item[2], item[3], date_time=datetime.strptime(item[1], "%m-%d-%y %H:%M:%S"))
            notes.append(note)

        return notes

    def backup(self):
        if count_backups(os.path.dirname(self.db_file)) < 10:
            if self.args.filename is None:
                timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
                new_filename = r"C:\sqlite\db\notes_" + timestamp + ".db"
            else:
                new_filename = os.path.join(os.path.dirname(self.db_file), self.args.filename)

            new_filename = new_filename.replace(".db", "") + ".db"
            print(f"BACKING UP {self.db_file} TO FILE {new_filename}")
            shutil.copy(self.db_file, new_filename)

    def restore(self):
        if self.args.filename is None:
            filename = get_newest_file(os.path.dirname(self.db_file))
        else:
            filename = os.path.join(os.path.dirname(self.db_file), self.args.filename)

        if os.path.exists(filename):
            print(f"RESTORING BACKUP FROM {filename}. REPLACING {self.db_file}")
            shutil.copy(filename, self.db_file)
            self.db_file = filename
        else:
            print(f"Failed to restore backup: {filename} cannot be found.")

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

def count_backups(dir):
    db_file_list = os.listdir(dir)
    count = 0
    for f in db_file_list:
        if re.search(r"notes_backup_.*", f) is not None:
            count += 1
    return count

def get_newest_file(dir):
    db_file_list = os.listdir(dir)
    for i, filename in enumerate(db_file_list):
        db_file_list[i] = os.path.join(dir, filename)
    return max(db_file_list, key=os.path.getctime)

def parse_args():
    # Read environment from command line args
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Test/Dev argument
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run the program against a test database for testing features')

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a note to the database')
    parser_add.add_argument('content', nargs='*', action='store', type=str, default=None,
                            help="Content of note")
    parser_add.add_argument('-c', '--category', default='General', action='store',
                            help="Choose a category for the note to be added under")

    # List command
    parser_list = subparsers.add_parser('list', help='List notes in the database')
    parser_list.add_argument('-a', '--all', action='store_true',
                             help="List all notes under given criteria")
    parser_list.add_argument('-q', '--quantity', nargs='?', action='store', default=5, type=int,
                             help="Specify the amount of results to list")
    parser_list.add_argument('-c', '--category', nargs='?', default=None, action='store',
                             help="Choose a category of notes to list")

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete one or multiple notes from the database')
    parser_delete.add_argument('delete_criteria', nargs='*', action='store', type=str)

    # Erase command
    parser_erase = subparsers.add_parser('erase', help='Delete all notes from the database')

    # Backup command
    parser_backup = subparsers.add_parser('backup', help='Backup the database. 10 backups are stored at a time')
    parser_backup.add_argument('-f', '--filename', action='store', default=None,
                               help='Choose a filename to use for the backup file. By default, the current timestamp will be used')

    # Restore command
    parser_restore = subparsers.add_parser('restore', help='Restore the database from a file. If --filename is not given, restore the latest backup')
    parser_restore.add_argument('-f', '--filename', action='store', default=None,
                               help='Specify a file to backup data from. If not specified, the latest backup file will be used')

    # Help command
    parser_help = subparsers.add_parser('help', help='Display help text')
    # parser_help.add_argument('help', nargs='?', action='store', default=False)

    # Search command
    parser_search = subparsers.add_parser('search', help='List notes matching search term')
    parser_search.add_argument('search_criteria', nargs='*', action='store', type=str)

    args = parser.parse_args()
    if args.test:
        print(args)
    if args.command == "help":
        parser.print_help()
        exit()
    return args


def range_parser(item_list):
    regex = r"(\d*)\W(\d*)"
    new_list = []
    for item in item_list:
        if item.isnumeric():
            new_list.append(int(item))
        else:
            match = re.search(regex, item)
            if match:
                minimum, maximum = match.groups()
                if minimum.isnumeric() and maximum.isnumeric():
                    for i in range(int(minimum), int(maximum) + 1):
                        new_list.append(int(i))
                else:
                    new_list.append(item)
    return new_list


if __name__ == "__main__":
    args = parse_args()
    # print(args)
    if args.test:
        db_file = r"C:\sqlite\db\notes_test.db"
    else:
        db_file = r"C:\sqlite\db\notes.db"
    scratchpad = ScratchPad(db_file, args)
    scratchpad.run()
    # scratchpad.add_note()
