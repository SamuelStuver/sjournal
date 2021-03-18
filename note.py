import argparse
from datetime import datetime
import sqlite3
from sqlite3 import Error


class ScratchPad:
    def __init__(self, db_file, args):
        self.db_file = db_file
        self.args = args
        self.create_connection()

    def handle_args(self):
        for command in ['list', 'preview', 'delete', 'clear']:
            func = getattr(self, command)
            value = getattr(self.args, command)
            if value:
                return func
        if self.args.message:
            return self.add_note
        # Default action
        return self.preview

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
        cursor.execute(
            f"INSERT INTO {table_name} (id, timestamp, category, content) VALUES (:id, :timestamp, :category, :content)",
            note.dict)
        self.connection.commit()

    def add_note(self):
        note_data = {"category": self.args.category, "content": self.args.message}
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
        cursor.execute(f"SELECT * FROM notes ORDER BY id DESC")
        for item in cursor.fetchall():
            note = Note(item[0], item[2], item[3], date_time=datetime.strptime(item[1], "%m-%d-%y %H:%M:%S"))
            print(note)

    def preview(self):
        N = 5
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM notes ORDER BY id DESC LIMIT {N}")
        for item in cursor.fetchall():
            note = Note(item[0], item[2], item[3], date_time=datetime.strptime(item[1], "%m-%d-%y %H:%M:%S"))
            print(note)

    def clear(self):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM notes')
        self.connection.commit()

    def delete(self):
        cursor = self.connection.cursor()
        id_to_delete = self.args.delete
        cursor.execute(f'DELETE FROM notes WHERE id={id_to_delete}')
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
    parser.add_argument('-c', '--category', default="General", action='store', help="Choose a category under which to put the note")
    parser.add_argument('-m', '--message', default=False, action='store', help="Enter the contents of the note")
    parser.add_argument('-l', '--list', default=False, action='store_true', help="List all notes in the database")
    parser.add_argument('-p', '--preview', default=False, action='store_true', help="List the most recent few notes")
    parser.add_argument('-d', '--delete', action='store', help="Delete a note with a given ID")
    parser.add_argument('-x', '--clear', action='store_true', help="Delete a all notes")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    db_file = r"C:\sqlite\db\notes.db"

    scratchpad = ScratchPad(db_file, args)
    scratchpad.run()
    # scratchpad.add_note()
