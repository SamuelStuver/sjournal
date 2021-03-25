import argparse
from datetime import datetime
import sqlite3
from sqlite3 import Error
import re


class ScratchPad:
    def __init__(self, db_file, args):
        self.db_file = db_file
        self.args = args
        self.create_connection()

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

    def insert_into_table(self, table_name, note):
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
        self.insert_into_table("notes", note)
        self.connection.commit()

    def list(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM notes ORDER BY id DESC"

        try:
            # Used explicit command and quantity is given
            quantity = int(self.args.quantity)
        except AttributeError:
            # Used default command, no quantity given. Assume list most recent 5
            quantity = 5
        except ValueError:
            # Used explicit command, but quantity given as non-integer
            if self.args.quantity == 'all':
                quantity = None

        if quantity:
            query += f" LIMIT {quantity}"
        cursor.execute(query)
        for item in cursor.fetchall():
            note = Note(item[0], item[2], item[3], date_time=datetime.strptime(item[1], "%m-%d-%y %H:%M:%S"))
            print(note)

    def delete(self):
        ids_to_delete = range_parser(self.args.delete_criteria)
        cursor = self.connection.cursor()
        for tagged_id in ids_to_delete:
            id = tagged_id[0]
            tag = tagged_id[1]
            if tag == 'exact':
                cursor.execute(f'DELETE FROM notes WHERE id={id}')
            elif tag == 'below':
                for i in range(0,id+1):
                    cursor.execute(f'DELETE FROM notes WHERE id={i}')
            elif tag == 'above':
                cursor.execute('SELECT max(id) FROM notes')
                max_id = cursor.fetchone()[0]
                for i in range(id,max_id+1):
                    cursor.execute(f'DELETE FROM notes WHERE id={i}')
        self.connection.commit()

    def clear(self):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM notes')
        self.connection.commit()


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
    parser_list.add_argument('quantity', nargs='?', action='store', default=5, type=str)

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete one or multiple notes from the database')
    parser_delete.add_argument('delete_criteria', nargs='*', action='store', type=str)

    # Erase command
    parser_erase = subparsers.add_parser('erase', help='Delete all notes from the database')

    # Help command
    parser_help = subparsers.add_parser('help', help='Display help text')
    # parser_help.add_argument('help', nargs='?', action='store', default=False)



    # Search command
    # parser_search = subparsers.add_parser('search', help='List notes matching search term')

    args = parser.parse_args()
    if args.command == "help":
        parser.print_help()
        exit()
    return args


def range_parser(item_list):
    regex_modifiers = {
        r"([0-9]+)\-([0-9]+)": "exact",
        r"([0-9]+)\:": "above",
        r"\:([0-9]+)": "below"
    }
    new_list = []
    for item in item_list:
        try:
            new_list.append((int(item), 'exact'))
        except ValueError as e:
            for regex in regex_modifiers.keys():
                match = re.search(regex, item)
                if match:
                    modifier = regex_modifiers[regex]
                    if modifier == 'exact':
                        minimum = int(match.group(1))
                        maximum = int(match.group(2))
                        for i in range(minimum, maximum+1):
                            new_list.append((i, modifier))
                    else:
                        val = int(match.group(1))
                        new_list.append((int(val), modifier))
    print("**** ", new_list)
    return new_list


if __name__ == "__main__":
    args = parse_args()
    if args.test:
        db_file = r"C:\sqlite\db\notes_test.db"
    else:
        db_file = r"C:\sqlite\db\notes.db"
    scratchpad = ScratchPad(db_file, args)
    scratchpad.run()
    # scratchpad.add_note()
