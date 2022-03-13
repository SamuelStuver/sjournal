import pytest
import subprocess
import argparse
import os
import random
import re
import json
import shutil
from sjournal import SJournal, Note
from utils_test import backup_file, delete_file, \
    get_project_root, \
    validate_note, validate_config, \
    random_string, random_hex_color
from logger import logger

# Suite of testing to validate the CLI interface for sjournal using subprocess to call the application

ROOT_DIR = get_project_root()
sjournal_py = f"{os.path.join(ROOT_DIR, 'sjournal.py')}"

n_gen_notes = 21
n_gen_categories = 3
n_gen_styles = 5


@pytest.fixture(scope="function")
def clean_journal():

    logger.info(f"setup clean journal at {os.path.join(ROOT_DIR, 'journals', 'automated_test.db')}")
    # backup current config file
    config_filename = os.path.join(ROOT_DIR, "config.json")
    backup_config_file = backup_file(config_filename)

    # if "automated_test.db" exists, delete it
    journal_file = os.path.join(ROOT_DIR, "journals", "automated_test.db")
    if os.path.isfile(journal_file):
        delete_file(journal_file)

    # create new test notebook
    args = argparse.Namespace(command="load", journal_name="automated_test", debug=False)
    journal = SJournal(args)
    journal.run()

    yield journal

    # delete notebook
    journal_file = os.path.join(ROOT_DIR, "journals", "automated_test.db")
    delete_file(journal_file)

    with open(config_filename, "r") as config_file:
        config = json.load(config_file)

    # restore config file
    backup_file(backup_config_file, config_filename)
    delete_file(backup_config_file)

    # delete any backups used for test
    backup_dir = os.path.join(ROOT_DIR, "journals", "backups", "automated_test")
    if os.path.isdir(backup_dir):
        shutil.rmtree(backup_dir)


@pytest.fixture(scope="function")
def fixed_notes_journal(clean_journal):
    journal = clean_journal

    categories = []
    for c in range(n_gen_categories):
        categories.append(f"Category {c}")

    for i in range(n_gen_notes):
        # journal.create_connection()
        category = categories[i % len(categories)]
        journal.args = argparse.Namespace(command="add", category=category, content=[f"Note {i}"], style="", debug=False)
        journal.run()

    yield journal


@pytest.fixture(scope="function")
def random_journal(clean_journal):
    journal = clean_journal

    # Generate random category names
    categories = []
    for c in range(n_gen_categories):
        categories.append(random_string(10))
    logger.debug(f"generated categores: {categories}")

    # Generate random styles
    styles = []
    for s in range(n_gen_styles):
        styles.append(f"bold {random_hex_color()}")
    logger.debug(f"generated styles: {styles}")

    # Populate journal
    for n in range(n_gen_notes):
        category = categories[n % len(categories)]
        # journal.create_connection()
        content = ' '.join([random_string(random.randint(1, 20)) for i in range(50)])
        journal.args = argparse.Namespace(command="add", category=category, content=[f"{content}"], style=random.choice(styles), debug=False)
        journal.run()

    yield journal


def test_load(clean_journal):
    # Start with clean empty journal
    journal = clean_journal
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
def test_add_note(clean_journal, command, expected):
    # Start with clean empty journal
    journal = clean_journal

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


def test_edit_note(fixed_notes_journal):
    # Start with a journal that contains a few notes
    journal = fixed_notes_journal
    notes = journal.notes

    # For each note, edit it and confirm that the note data updates
    for note in notes[::-1]:

        # Execute Command with subsequent input
        logger.info(f"EDIT NOTE {note.id}")

        proc = subprocess.Popen(['python', sjournal_py, 'edit', f'{note.id}'.strip()], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        result = proc.communicate(input=b'EDITED')

        logger.debug(result)

        # Confirm successful command
        assert proc.returncode == 0

        # Confirm that the note at note_id has been edited successfully
        expected = {"category": note.category, "content": f"EDITED", "id": note.id}
        validate_note(journal.notes[note.id], expected)


def test_delete_note(fixed_notes_journal):
    # Start with a journal that contains a few notes
    journal = fixed_notes_journal
    original_notes = journal.notes

    # Starting journal should have 3 notes
    logger.info("Journal should have 3 notes")
    assert journal.length == n_gen_notes

    # Delete the most recent note via the commandline until empty
    for note in original_notes[::-1]:
        logger.info(f"Delete note #{note.id}")

        # Execute Command
        commandline = f'python {sjournal_py} delete {note.id}'
        result = subprocess.run(commandline, capture_output=True)

        logger.debug(f"stdout: {result.stdout}")

        # Confirm successful command
        assert result.returncode == 0

        # Confirm that the journal has 1 fewer note, and that the most recent note is the previous one
        logger.debug(journal.notes)
        assert journal.length == note.id, f"# of Notes is {journal.length} after deleting note {note.id}. Expected length of {note.id}"
        if journal.length > 0:
            # Most recent note has the correct data
            assert journal.notes[-1] == original_notes[note.id-1]


@pytest.mark.parametrize('command', [
        '',
        'list',
        'list 10',
        'list -a',
        'list -r',
        'list -c',
        'list 10 -a',
        'list 10 -r',
        'list 10 -c',
        'list -a -r',
        'list -a -c',
        'list -r -c',
        'list 10 -a -r',
        'list 10 -a -c',
        'list 10 -r -c',
        'list -a -r -c',
        'list 10 -a -r -c',
])
def test_list_default(random_journal, command):

    journal = random_journal
    notes = journal.notes

    commandline = f"python {sjournal_py} --debug " + command

    n_printed = 5
    if '-c' in command:
        # Get one category and determine the number of notes and number to print. will print 5 if more than 5 notes
        all_categories = list(set([note.category for note in notes]))
        commandline += f' "{all_categories[0]}"'
        notes = [note for note in notes if note.category == all_categories[0]]
        if len(notes) < 5:
            n_printed = len(notes)
    if '10' in command:
        n_printed = 10
    if '-a' in command:
        n_printed = len(notes)

    # List notes via commandline with debug option
    logger.info(f"List notes via commandline")
    logger.debug(f"commandline: {commandline}")
    logger.debug(f"For this command, expect {n_printed} notes")

    result = subprocess.run(commandline, capture_output=False)
    logger.debug(result)
    assert result.returncode == 0

    # Read debug text into string
    debug_file = os.path.join(ROOT_DIR, "reports", "debug.log")
    with open(debug_file, "r") as output_file:
        full_text = output_file.read()

    logger.debug(full_text)

    # Search output text for table headers
    header = rf"ID\s+\|\s+Timestamp\s+\|\s+Category\s+\|\s+Content\s+"
    match = re.search(header, full_text)
    assert match, f"Could not find header in debug output"
    logger.debug(match.group(0))

    # Search output text for each note
    for i, note in enumerate(notes[-n_printed:]):
        regex = rf"{note.id}.*{note.timestamp}.*{note.category}.*{note.content[14:24]}"
        match = re.search(regex, full_text)
        assert match, f"Could not find Note # {note.id} in debug output\n{regex}"
        logger.debug(match.group(0))


@pytest.mark.parametrize('command', [
        'categories',
        'categories -s',
])
def test_categories(random_journal, command):
    journal = random_journal
    notes = journal.notes
    expected_categories = list(set([note.category for note in notes]))

    # List categories via command line
    commandline = f"python {sjournal_py} --debug " + command
    if "-s" in command:
        commandline += f' "{expected_categories[0]}"'
        expected_categories = [expected_categories[0]]

    logger.debug(commandline)
    result = subprocess.run(commandline, capture_output=False)
    logger.debug(result)
    assert result.returncode == 0

    # Read debug text into string
    debug_file = os.path.join(ROOT_DIR, "reports", "debug.log")
    with open(debug_file, "r") as output_file:
        full_text = output_file.read()

    logger.debug(full_text)

    # Search output text for each category
    for category in expected_categories:
        regex = rf"{category}"
        match = re.search(regex, full_text)
        assert match, f"Could not find category {category} in debug output"
        logger.debug(match.group(0))


@pytest.mark.parametrize('command', [
        'backup',
        'backup -f delete_this_backup',
])
def test_backup(random_journal, command):
    # Start with populated journal
    original_journal = random_journal
    original_notes = original_journal.notes

    # Backup journal via command line
    commandline = f"python {sjournal_py} " + command
    if "-f" in command:
        expected_backup_filename = command.split()[-1]
    else:
        expected_backup_filename = "backup_automated_test"

    logger.debug(commandline)
    result = subprocess.run(commandline, capture_output=False)
    logger.debug(result)
    assert result.returncode == 0

    # Verify that the backup exists
    backup_dir = os.path.join(ROOT_DIR, "journals", "backups", "automated_test")
    assert os.path.isdir(backup_dir)

    with os.scandir(backup_dir) as dir_contents:
        match = [entry for entry in dir_contents if expected_backup_filename in entry.name]

    logger.debug(match)
    # Should be only one match since we started with no backup
    assert len(match) == 1
    backup_entry = match[0]
    assert backup_entry.is_file()

    backup_journal_filename = os.path.splitext(backup_entry.name)[0]
    logger.info(f"found backup {backup_journal_filename}")

    # Load the backup and confirm that all original notes are present
    # Change config file to reflect backup location
    config_file_path = os.path.join(ROOT_DIR, "config.json")
    config = {
        "journal_dir": os.path.join("journals", "backups", "automated_test"),
        "journal_name": backup_journal_filename
    }
    confstring = json.dumps(config)
    with open(config_file_path, "w") as config_file:
        config_file.write(confstring)

    # load backup
    args = argparse.Namespace(command="load", journal_name=backup_journal_filename, debug=False)
    new_journal = SJournal(args)
    new_journal.run()

    # confirm that all original notes are present
    for i, note in enumerate(new_journal.notes):
        assert note == original_notes[i], f"New Note does not equal old Note:\nNew: {note}\nOld: {original_notes[i]}"


@pytest.mark.parametrize('command, action', [
        ('restore', 'erase'),
        ('restore -f delete_this_backup', 'erase'),
        ('restore', 'delete'),
        ('restore -f delete_this_backup', 'delete'),
        # ('restore', 'delete -j'),
        # ('restore -f delete_this_backup', 'delete -j'),
])
def test_restore(random_journal, command, action):
    # Start with populated journal
    original_journal = random_journal
    original_notes = original_journal.notes

    # Backup the journal
    if "-f" in command:
        filename = command.split()[-1]
    else:
        filename = None
    args = argparse.Namespace(command='backup', debug=False, filename=filename)
    original_journal.args = args
    original_journal.run()

    # Screw up the journal via 'action', confirm that the journal is empty
    if "delete" in action:
        if "-j" in action:
            args = argparse.Namespace(command='delete', debug=False, journal_name="automated_test")
            original_journal.args = args
            original_journal.run()
        else:
            args = argparse.Namespace(command='delete', debug=False, delete_criteria=[f"{original_notes[0].id}-{original_notes[-1].id}"])
            original_journal.args = args
            original_journal.run()
    else:
        args = argparse.Namespace(command=action, debug=False)
        original_journal.args = args
        original_journal.run()

    assert original_journal.length == 0

    # Restore the journal
    commandline = f"python {sjournal_py} " + command
    logger.debug(commandline)
    result = subprocess.run(commandline, capture_output=False)
    logger.debug(result)
    assert result.returncode == 0

    # Confirm that the notes are back
    for i, note in enumerate(original_journal.notes):
        logger.debug(f"\nNew: {note}\nOld: {original_notes[i]}")
        assert note == original_notes[i], f"New Note does not equal old Note:\nNew: {note}\nOld: {original_notes[i]}"


def test_erase(random_journal):
    journal = random_journal
    assert journal.length == n_gen_notes

    # Erase the notebook via the command line
    commandline = f"python {sjournal_py} --debug erase"
    logger.debug(commandline)
    result = subprocess.run(commandline, capture_output=False)
    logger.debug(result)
    assert result.returncode == 0
    assert journal.length == 0


@pytest.mark.parametrize('command', [
        'search Note 1',
        'search',
])
def test_search(fixed_notes_journal, command):
    # Start with populated, non-random journal
    journal = fixed_notes_journal
    notes = journal.notes
    for note in notes:
        logger.debug(note)
    # Search the notes via commandline with debug
    commandline = f"python {sjournal_py} --debug " + command

    if "Note" not in command:
        for i, note in enumerate(notes):
            # send command
            commandline = f"python {sjournal_py} --debug {command} {i}"
            result = subprocess.run(commandline, capture_output=False)
            logger.debug(result)
            assert result.returncode == 0

            # Read debug text into string
            debug_file = os.path.join(ROOT_DIR, "reports", "debug.log")
            with open(debug_file, "r") as output_file:
                full_text = output_file.read()

            logger.debug(full_text)

            # Search output text for the searched note
            regex = rf"{note.id}.*{note.timestamp}.*{note.category}.*{note.content[14:24]}"
            match = re.search(regex, full_text)
            assert match, f"Could not find Note # {note.id} in debug output\n{regex}"
            logger.debug(match.group(0))

    else:
        # send command
        result = subprocess.run(commandline, capture_output=False)
        logger.debug(result)
        assert result.returncode == 0

        # Read debug text into string
        debug_file = os.path.join(ROOT_DIR, "reports", "debug.log")
        with open(debug_file, "r") as output_file:
            full_text = output_file.read()

        logger.debug(full_text)

        search_term = command.split("search ")[-1]
        expected_notes = [note for note in notes if search_term in note.content]
        # Search output text for each note
        for note in expected_notes:
            regex = rf"{note.id}.*{note.timestamp}.*{note.category}.*{note.content}"
            match = re.search(regex, full_text)
            assert match, f"Could not find Note # {note.id} in debug output\n{regex}"
            logger.debug(match.group(0))