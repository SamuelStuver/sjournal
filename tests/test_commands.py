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
        journal.args = argparse.Namespace(command="add", category="General", content=[f"Note {i+1}"], style="")
        journal.run()

    yield journal


def test_load(clean_journal_fixture):
    journal = clean_journal_fixture
    logger.info("Clean journal should have the correct name")
    assert journal.journal_name == "automated_test"

    logger.info("Clean journal should have 0 notes")
    notes = journal._get_notes()
    assert len(notes) == 0

    validate_config({"journal_dir": "journals", "journal_name": "automated_test"})

    logger.info("Load a new journal named 'delete_this_journal'")
    commandline = f'python {sjournal_py} load delete_this_journal'
    result = subprocess.run(commandline, capture_output=True)
    logger.debug(f"stdout: {result.stdout}")
    assert result.returncode == 0

    validate_config({"journal_dir": "journals", "journal_name": "delete_this_journal"})

    logger.info("Delete the new journal file")
    new_journal_file = os.path.join(ROOT_DIR, "journals", "delete_this_journal.db")
    delete_file(new_journal_file)


@pytest.mark.parametrize('commandline, expected', [
        (f'python {sjournal_py} add ""',
         {"category":"General", "content":"", "id":1}),

        (f'python {sjournal_py} add Hello World',
         {"category":"General", "content":"Hello World", "id":1}),
        (f'python {sjournal_py} add "Hello World"',
         {"category":"General", "content":"Hello World", "id":1}),

        (f'python {sjournal_py} add -c "Test" Hello World',
         {"category":"Test", "content":"Hello World", "id":1}),
        (f'python {sjournal_py} add -c "Test" "Hello World"',
         {"category":"Test", "content":"Hello World", "id":1}),

        (f'python {sjournal_py} add -s "bold red" "Hello World"',
         {"category":"General", "content":"[bold red]Hello World[/]", "id":1}),
    ])
def test_add_note(clean_journal_fixture, commandline, expected):
    journal = clean_journal_fixture

    logger.info("Add note via commandline")
    logger.debug(f"commandline: {commandline}")
    result = subprocess.run(commandline, capture_output=False)
    assert result.returncode == 0

    logger.info("Journal should have 1 note")
    notes = journal._get_notes()
    assert len(notes) == 1
    logger.debug(notes[0])

    validate_note(notes[0], expected)


def test_edit_note():
    pytest.skip("TODO")


def test_delete_note(journal_with_notes_fixture):
    journal = journal_with_notes_fixture

    logger.info("Journal should have 3 notes")
    notes = journal._get_notes()
    assert len(notes) == 3

    for note_id in [3, 2, 1]:
        logger.info(f"Delete note #{note_id}")
        commandline = f'python {sjournal_py} delete {note_id}'
        result = subprocess.run(commandline, capture_output=True)
        logger.debug(f"stdout: {result.stdout}")
        assert result.returncode == 0

        notes = journal._get_notes()
        logger.debug(notes)
        assert len(notes) == note_id - 1
        if len(notes) > 0:
            expected = {"category": "General", "content": f"Note {note_id - 1}", "id": note_id - 1}
            validate_note(notes[-1], expected)


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
    