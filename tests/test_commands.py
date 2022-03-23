import pytest
import subprocess
import argparse
import os
import random
import re
import json
import shutil
from platform import system
from src.sjournal import SJournal
from utils_test import backup_file, delete_file, \
    validate_note, validate_config, \
    random_string, random_hex_color, \
    send_cli_command, read_debug, \
    output_contains_note, output_contains_text
from logger import logger

# Suite of tests to validate the CLI interface for sjournal using subprocess to call the application

n_gen_notes = 21
n_gen_categories = 3
n_gen_styles = 5


@pytest.fixture(scope="function")
def clean_journal(environment):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Make the reports directory in ~/sjournal/ if it does not exist
    if not os.path.isdir(os.path.dirname(DEBUG_OUTPUT)):
        os.makedirs(os.path.dirname(DEBUG_OUTPUT))

    logger.info(f"setup clean journal at {os.path.join(HOME_DIR, 'sjournal', 'journals', 'automated_test.db')}")
    # backup current config file if one exists
    config_filename = os.path.join(SJOURNAL_DIR, "sjournal_config.json")
    if os.path.isfile(config_filename):
        backup_config_file = backup_file(config_filename)
        config_file_existed = True
    else:
        backup_config_file = False
        config_file_existed = False

    # if "automated_test.db" exists, delete it
    journal_file = os.path.join(SJOURNAL_DIR, "journals", "automated_test.db")
    if os.path.isfile(journal_file):
        delete_file(journal_file)

    # create new test notebook
    args = argparse.Namespace(command="load", journal_name="automated_test", debug=False)
    journal = SJournal(args)
    journal.run()

    yield journal

    # delete notebook
    journal_file = os.path.join(SJOURNAL_DIR, "journals", "automated_test.db")
    delete_file(journal_file)

    # restore default config file
    if config_file_existed:
        backup_file(backup_config_file, config_filename)
        delete_file(backup_config_file)
    else:
        config = {
            "journal_dir": os.path.join(HOME_DIR, "sjournal", "journals"),
            "journal_name": "notes"
        }
        confstring = json.dumps(config)
        with open(config_filename, "w") as config_file:
            config_file.write(confstring)

    # delete any backups used for test
    backup_dir = os.path.join(SJOURNAL_DIR, "journals", "backups", "automated_test")
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
def split_categories_journal(clean_journal):
    journal = clean_journal

    categories = ["General", "Category X", "Category 0"]

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


def test_load(clean_journal, environment):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with clean empty journal
    journal = clean_journal
    logger.info("Clean journal should have the correct name")
    assert journal.journal_name == "automated_test"

    # Clean journal should be empty
    logger.info("Clean journal should have 0 notes")
    assert journal.length == 0

    # Verify that the correct config info is used with starting journal
    validate_config({"journal_dir": os.path.join(SJOURNAL_DIR, "journals"), "journal_name": "automated_test"})

    # Load a new journal
    logger.info("Load a new journal named 'delete_this_journal'")
    commandline = f'{sjournal_exec} load delete_this_journal'
    result = send_cli_command(commandline, assert_okay=True, user_input=None)
    expected_journal_file = os.path.join(SJOURNAL_DIR, "journals", "delete_this_journal.db")
    assert output_contains_text(result.stdout, rf"Set journal to {expected_journal_file}")

    # Verify that the correct config info is used with new journal
    validate_config({"journal_dir": os.path.join(SJOURNAL_DIR, "journals"), "journal_name": "delete_this_journal"})

    # Load an existing journal
    logger.info("Load an existing journal: 'automated_test'")
    commandline = f'{sjournal_exec} load automated_test'
    result = send_cli_command(commandline, assert_okay=True, user_input=None)
    expected_journal_file = os.path.join(SJOURNAL_DIR, "journals", "automated_test.db")
    assert output_contains_text(result.stdout, rf"Set journal to {expected_journal_file}")

    # Verify that the correct config info is used with new journal
    validate_config({"journal_dir": os.path.join(SJOURNAL_DIR, "journals"), "journal_name": "automated_test"})

    # Delete the new journal
    logger.info("Delete the new journal file")
    new_journal_file = os.path.join(SJOURNAL_DIR, "journals", "delete_this_journal.db")
    delete_file(new_journal_file)


@pytest.mark.parametrize('command, expected_data', [
        (f'add ""',
         {"category":"General", "content":"", "id":0, "style":""}),

        (f'add Hello World',
         {"category":"General", "content":"Hello World", "id":0, "style":""}),
        (f'add "Hello World"',
         {"category":"General", "content":"Hello World", "id":0, "style":""}),

        (f'add -c "Test" Hello World',
         {"category":"Test", "content":"Hello World", "id":0, "style":""}),
        (f'add -c "Test" "Hello World"',
         {"category":"Test", "content":"Hello World", "id":0, "style":""}),

        (f'add -s "bold red" "Hello World"',
         {"category":"General", "content":"Hello World", "id":0, "style":"bold red"}),
])
def test_add_note(clean_journal, environment, command, expected_data):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with clean empty journal
    journal = clean_journal
    for i in range(10):

        # Add note via commandline
        logger.info(f"Add note {i} via commandline")
        commandline = f"{sjournal_exec} " + command
        result = send_cli_command(commandline, assert_okay=True, user_input=None)
        assert result.stdout == result.stderr == ""

        # Journal should have one more note
        logger.info(f"Journal should have {i+1} note(s)")
        assert journal.length == i+1

        # Verify that the latest note has the correct data
        expected_data_i = expected_data
        expected_data_i["id"] = i
        validate_note(journal.latest, expected_data_i)


def test_edit_note(fixed_notes_journal, environment):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with a journal that contains a few notes
    journal = fixed_notes_journal
    notes = journal.notes

    # For each note, edit it and confirm that the note data updates
    for note in notes[::-1]:

        # Execute Command with subsequent input
        logger.info(f"EDIT NOTE {note.id}")
        # try:
        #     # depending on environment, sjournal_exec might only be one item instead of 2. sjournal vs python run.py
        #     process_args = [sjournal_exec.split()[0], sjournal_exec.split()[1], 'edit', f'{note.id}'.strip()]
        # except IndexError:
        #     process_args = [sjournal_exec, 'edit', f'{note.id}'.strip()]
        #
        # if system() == 'Linux':
        #     process_args = [sjournal_exec + ' edit ' + f'{note.id}'.strip()]
        #
        # logger.info(process_args)
        #
        # proc = subprocess.Popen(process_args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # result = proc.communicate(input=b'EDITED')
        #
        # logger.debug(proc)
        # logger.debug(result)
        #
        # # Confirm successful command
        # assert proc.returncode == 0, proc

        commandline = f'{sjournal_exec} edit {note.id}'
        user_input = "EDITED"
        result = send_cli_command(commandline, assert_okay=True, user_input=user_input)
        expected_output = f'Editing Note #{note.id}.*"Note {note.id}"Enter new note text.*Note {note.id}.*'
        assert output_contains_text(result.stdout, expected_output)

        # Confirm that the note at note_id has been edited successfully
        expected = {"category": note.category, "content": f"EDITED", "id": note.id}
        validate_note(journal.notes[note.id], expected)

    logger.debug(journal.notes)


def test_delete_note(fixed_notes_journal, environment):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with a journal that contains a few notes
    journal = fixed_notes_journal
    original_notes = journal.notes

    # Starting journal should have {n_gen_notes} notes
    logger.info(f"Journal should have {n_gen_notes} notes")
    assert journal.length == n_gen_notes

    # Delete the most recent note via the commandline until empty
    for note in original_notes[::-1]:
        logger.info(f"Delete note #{note.id}")

        # Execute Command
        commandline = f'{sjournal_exec} delete {note.id}'
        result = send_cli_command(commandline, assert_okay=True, user_input=None)
        assert output_contains_text(result.stdout, f"DELETED NOTE #{note.id}")

        # Confirm that the journal has 1 fewer note, and that the most recent note is the previous one
        assert journal.length == note.id, f"# of Notes is {journal.length} after deleting note {note.id}. Expected length of {note.id}"
        if journal.length > 0:
            # Most recent note has the correct data
            assert journal.latest == original_notes[note.id-1]


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
def test_list_notes(random_journal, environment, command):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    journal = random_journal
    notes = journal.notes

    commandline = f"{sjournal_exec} " + command

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

    result = send_cli_command(commandline, assert_okay=True, user_input=None)
    assert output_contains_text(result.stdout, rf"ID.*Timestamp.*Category.*Content")

    # Search output text for each note
    for i, note in enumerate(notes[-n_printed:]):
        assert output_contains_note(result.stdout, note)


@pytest.mark.parametrize('command', [
        'categories',
        'categories -s',
])
def test_categories(random_journal, environment, command):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    journal = random_journal
    notes = journal.notes
    expected_categories = list(set([note.category for note in notes]))

    # List categories via command line
    commandline = f"{sjournal_exec} " + command
    if "-s" in command:
        commandline += f' "{expected_categories[0]}"'
        expected_categories = [expected_categories[0]]

    result = send_cli_command(commandline, assert_okay=True, user_input=None)

    # Search output text for each category
    for category in expected_categories:
        assert output_contains_text(result.stdout, category)


@pytest.mark.parametrize('command', [
        'backup',
        'backup -f delete_this_backup',
])
def test_backup(random_journal, environment, command):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with populated journal
    original_journal = random_journal
    original_notes = original_journal.notes

    # Backup journal via command line
    commandline = f"{sjournal_exec} " + command
    if "-f" in command:
        expected_backup_filename = command.split()[-1]
    else:
        expected_backup_filename = "backup_automated_test"

    result = send_cli_command(commandline, assert_okay=True, user_input=None)
    expected_output = rf"BACKING UP.*.dbTO FILE.*{expected_backup_filename}.*.db"
    assert output_contains_text(result.stdout, expected_output)

    # Verify that the backup exists
    backup_dir = os.path.join(SJOURNAL_DIR, "journals", "backups", "automated_test")
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
    config_file_path = os.path.join(SJOURNAL_DIR, "sjournal_config.json")
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
def test_restore(random_journal, environment, command, action):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with populated journal
    original_journal = random_journal
    original_notes = original_journal.notes

    # Backup the journal
    if "-f" in command:
        backup_filename = command.split()[-1]
    else:
        backup_filename = None
    args = argparse.Namespace(command='backup', debug=False, filename=backup_filename)
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
        args = argparse.Namespace(command=action, debug=False, force=True)
        original_journal.args = args
        original_journal.run()

    assert original_journal.length == 0

    # Restore the journal
    commandline = f"{sjournal_exec} " + command
    result = send_cli_command(commandline, assert_okay=True, user_input=None)
    expected_output = rf"RESTORING BACKUP FROM.*.dbREPLACING.*{original_journal.journal_name}.*.db"
    assert output_contains_text(result.stdout, expected_output)

    # Confirm that the notes are back
    for i, note in enumerate(original_journal.notes):
        logger.debug(f"\nNew: {note}\nOld: {original_notes[i]}")
        assert note == original_notes[i], f"New Note does not equal old Note:\nNew: {note}\nOld: {original_notes[i]}"


@pytest.mark.parametrize('user_input', [
        'y',
        'n',
        'Y',
        'N'
])
def test_erase(random_journal, environment, user_input):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    journal = random_journal
    assert journal.length == n_gen_notes

    # Erase the notebook via the command line
    commandline = f"{sjournal_exec} erase"
    result = send_cli_command(commandline, assert_okay=True, user_input=user_input)
    if user_input == 'y' or user_input == 'Y':
        assert output_contains_text(result.stdout, "All notes deleted.")
        assert journal.length == 0
    elif user_input == 'n' or user_input == 'N':
        assert output_contains_text(result.stdout, "No notes were deleted.")
        assert journal.length == n_gen_notes


def test_search_all_notes(fixed_notes_journal, environment):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with populated, non-random journal
    journal = fixed_notes_journal
    notes = journal.notes

    for i, note in enumerate(notes):
        notes_with_number = [note for note in notes if str(i) in note.content]
        logger.debug(f"For number {i}, there should be {len(notes_with_number)} notes that match")

        # search for each note by number
        commandline = f"{sjournal_exec} search {i}"
        result = send_cli_command(commandline)

        # Confirm that the command output contains the expected note(s)
        for matching_note in notes_with_number:
            assert output_contains_note(result.stdout, matching_note)


def test_search_random_notes(random_journal, environment):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with populated, random journal
    journal = random_journal
    notes = journal.notes

    for i, note in enumerate(notes):
        # workaround until style is split from content - just gets the raw note content
        raw_content = note.content# .split(']')[1].split('[')[0]

        # search for the first, middle, and last word in the note and confirm that matching notes are found
        words = raw_content.split()
        words = [words[0], words[len(words)//2], words[-1]]
        for word in words:
            notes_with_word = [note for note in notes if word in note.content]
            logger.debug(f"For word {word}, there should be {len(notes_with_word)} notes that match")

            # send command
            commandline = f"{sjournal_exec} search {word}"
            result = send_cli_command(commandline)

            # Search output text for the expected note(s)
            for matching_note in notes_with_word:
                assert output_contains_note(result.stdout, matching_note)


def test_search_by_category(fixed_notes_journal, environment):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with populated, random journal
    journal = fixed_notes_journal
    notes = journal.notes

    # log all notes
    logger.debug("\n" + "\n".join([str(note) for note in notes]))

    categories = set(note.category for note in notes)

    for category in categories:
        notes_with_category = [note for note in notes if note.category == category]

        logger.debug(f"For category {category}, there should be {len(notes_with_category)} notes")

        for i in range(len(notes)):
            matching_notes = [note for note in notes_with_category if str(i) in note.content]
            logger.debug(f"If searching for '{i}' in category '{category}', there should be {len(matching_notes)} notes")

            # send command
            commandline = f'{sjournal_exec} search -c "{category}" "{i}"'
            result = send_cli_command(commandline)

            # Search output text for the expected note(s)
            for matching_note in matching_notes:
                assert output_contains_note(result.stdout, matching_note)


@pytest.mark.xfail
@pytest.mark.parametrize('command, should_pass', [
        ("list -c '<CATEGORY>'", True),
        ("list -c '<CATEGORY>", False),
        ("list -c <CATEGORY>'", False),
        ("list -c <CATEGORY>\"", False),

        ("search -c '<CATEGORY>' \" \"", True),
        ("search -c '<CATEGORY> \" \"", False),
        ("search -c <CATEGORY>' \" \"", False),
        ("search -c <CATEGORY>\" \" \"", False),
])
def test_quotation_marks_withspace(split_categories_journal, environment, command, should_pass):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with populated, random journal
    journal = split_categories_journal
    notes = journal.notes

    # log all notes
    logger.debug("\n" + "\n".join([str(note) for note in notes]))

    categories = ["Category X", "Category 0"]
    for category in categories:
        notes_with_category = [note for note in notes if note.category == category]
        logger.debug(f"For category {category}, there should be {len(notes_with_category)} notes")

        commandline = rf"{sjournal_exec} {command.replace('<CATEGORY>', category)}"

        # send command
        if should_pass:
            result = send_cli_command(commandline, assert_okay=True)

            # Search output text for the expected note(s)
            for matching_note in notes_with_category:
                assert output_contains_note(result.stdout, matching_note)

        else:
            result = send_cli_command(commandline, assert_okay=False)
            assert result.returncode != 0
            assert output_contains_text(result.stderr, "Invalid Category Name.")


@pytest.mark.xfail
@pytest.mark.parametrize('command, should_pass', [
        ("list -c 'General'", True),
        ("list -c 'General", False),
        ("list -c General'", False),
        ("list -c General\"", True),

        ("search -c 'General' \" \"", True),
        ("search -c 'General \" \"", False),
        ("search -c General' \" \"", False),
        ("search -c General\" \" \"", True),
])
def test_quotation_marks_nospace(split_categories_journal, environment, command, should_pass):
    ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec = environment

    # Start with populated, random journal
    journal = split_categories_journal
    notes = journal.notes

    # log all notes
    logger.debug("\n" + "\n".join([str(note) for note in notes]))

    notes_with_category = [note for note in notes if note.category == "General"]
    logger.debug(f"For category General, there should be {len(notes_with_category)} notes")

    commandline = rf"{sjournal_exec} {command}"

    # send command
    if should_pass:
        result = send_cli_command(commandline, assert_okay=True)

        # Search output text for the expected note(s)
        for matching_note in notes_with_category:
            assert output_contains_note(result.stdout, matching_note)

    else:
        result = send_cli_command(commandline, assert_okay=False)
        assert result.returncode != 0
        assert output_contains_text(result.stderr, "Invalid Category Name.")