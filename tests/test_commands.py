import pytest
import subprocess
import argparse
import os
from sjournal import SJournal, Note
from utils_test import backup_file, delete_file, get_project_root, validate_note, validate_config
from logger import logger

# Suite of tests to validate the CLI interface for sjournal using subprocess to call the application

ROOT_DIR = get_project_root()
sjournal_py = f"{os.path.join(ROOT_DIR, 'sjournal.py')}"


@pytest.fixture(scope="function")
def clean_journal_fixture():

    logger.info(f"setup clean journal at {os.path.join(ROOT_DIR, 'journals', 'automated_test.db')}")
    # backup current config file
    config_file = os.path.join(ROOT_DIR, "config.json")
    backup_config_file = backup_file(config_file)

    # if "automated_test.db" exists, delete it
    journal_file = os.path.join(ROOT_DIR, "journals", "automated_test.db")
    delete_file(journal_file)

    # create new test notebook
    args = argparse.Namespace(command="load", journal_name="automated_test")
    journal = SJournal(args)
    journal.run()

    yield journal

    # delete notebook
    journal_file = os.path.join(ROOT_DIR, "journals", "automated_test.db")
    delete_file(journal_file)

    # restore config file
    backup_file(backup_config_file, config_file)
    delete_file(backup_config_file)


@pytest.fixture(scope="function")
def journal_with_notes_fixture(clean_journal_fixture):
    journal = clean_journal_fixture

    for i in range(3):
        journal.create_connection()
        journal.args = argparse.Namespace(command="add", category="General", content=[f"Note {i}"], style="")
        journal.run()

    yield journal


def test_load(clean_journal_fixture):
    # Start with clean empty journal
    journal = clean_journal_fixture
    logger.info("Clean journal should have the correct name")
    assert journal.journal_name == "automated_test"

    # Clean journal should be empty
    logger.info("Clean journal should have 0 notes")
    assert journal.length == 0

    # Verify that the correct config info is used with starting journal
    validate_config({"journal_dir": "journals", "journal_name": "automated_test"})

    # Load a new journal
    logger.info("Load a new journal named 'delete_this_journal'")
    commandline = f'python {sjournal_py} load delete_this_journal'
    result = subprocess.run(commandline, capture_output=True)
    logger.debug(f"stdout: {result.stdout}")
    assert result.returncode == 0

    # Verify that the correct config info is used with new journal
    validate_config({"journal_dir": "journals", "journal_name": "delete_this_journal"})

    # Delete the new journal
    logger.info("Delete the new journal file")
    new_journal_file = os.path.join(ROOT_DIR, "journals", "delete_this_journal.db")
    delete_file(new_journal_file)


@pytest.mark.parametrize('command, expected', [
        (f'add ""',
         {"category":"General", "content":"", "id":0}),

        (f'add Hello World',
         {"category":"General", "content":"Hello World", "id":0}),
        (f'add "Hello World"',
         {"category":"General", "content":"Hello World", "id":0}),

        (f'add -c "Test" Hello World',
         {"category":"Test", "content":"Hello World", "id":0}),
        (f'add -c "Test" "Hello World"',
         {"category":"Test", "content":"Hello World", "id":0}),

        (f'add -s "bold red" "Hello World"',
         {"category":"General", "content":"[bold red]Hello World[/]", "id":0}),
    ])
def test_add_note(clean_journal_fixture, command, expected):
    # Start with clean empty journal
    journal = clean_journal_fixture

    for i in range(5):
        # Add note via commandline
        logger.info(f"Add note {i} via commandline")

        commandline = f"python {sjournal_py} " + command

        logger.debug(f"commandline: {commandline}")
        result = subprocess.run(commandline, capture_output=False)
        assert result.returncode == 0

        # Journal should have one more note
        logger.info(f"Journal should have {i+1} note(s)")
        assert journal.length == i+1

        # Verify that the note has the correct data
        expected_i = expected
        expected_i["id"] = i
        validate_note(journal.notes[-1], expected_i)


def test_edit_note(journal_with_notes_fixture):
    # Start with a journal that contains a few notes
    journal = journal_with_notes_fixture

    # For each note, edit it and confirm that the note data updates
    for note_id in range(journal.length-1, -1, -1):

        # Execute Command with subsequent input
        logger.info(f"EDIT NOTE {note_id}")

        proc = subprocess.Popen(['python', sjournal_py, 'edit', f'{note_id}'.strip()], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        result = proc.communicate(input=b'EDITED')

        logger.debug(result)
        logger.debug(journal.notes)

        # Confirm successful command
        assert proc.returncode == 0

        # Confirm that the note at note_id has been edited successfully
        expected = {"category": "General", "content": f"EDITED", "id": note_id}
        validate_note(journal.notes[note_id], expected)


def test_delete_note(journal_with_notes_fixture):
    # Start with a journal that contains a few notes
    journal = journal_with_notes_fixture

    # Starting journal should have 3 notes
    logger.info("Journal should have 3 notes")
    assert journal.length == 3

    # Delete the most recent note via the commandline until empty
    full_length = journal.length
    for note_id in range(full_length-1, -1, -1):
        logger.info(f"Delete note #{note_id}")

        # Execute Command
        commandline = f'python {sjournal_py} delete {note_id}'
        result = subprocess.run(commandline, capture_output=True)

        logger.debug(f"stdout: {result.stdout}")

        # Confirm successful command
        assert result.returncode == 0

        # Confirm that the journal has 1 fewer note, and that the most recent note is the previous one
        logger.debug(journal.notes)
        assert journal.length == note_id, f"# of Notes is {journal.length} after deleting note {note_id}. Expected length of {note_id}"
        if journal.length > 0:
            # Most recent note has the correct data
            expected = {"category": "General", "content": f"Note {note_id - 1}", "id": note_id - 1}
            validate_note(journal.notes[-1], expected)


def test_list():
    pytest.skip("TODO")


def test_categories():
    pytest.skip("TODO")


def test_backup():
    pytest.skip("TODO")


def test_restore():
    pytest.skip("TODO")


def test_erase():
    pytest.skip("TODO")


def test_search():
    pytest.skip("TODO")


def test_help():
    pytest.skip("TODO")
    