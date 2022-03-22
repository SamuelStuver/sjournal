import shutil
import os
import json
import random
import string
import subprocess
import re
from logger import logger


def get_project_root():
    return os.path.abspath(os.curdir)


def backup_file(file_path, new_path=None):
    ext = os.path.splitext(file_path)[1]
    if not new_path:
        new_path = f"{os.path.splitext(file_path)[0]}_backup{ext}"

    shutil.copyfile(file_path, new_path)
    logger.debug(f"backed up file {file_path} to {new_path}")
    return new_path


def delete_file(file_path):
    if os.path.isfile(file_path):

        os.remove(file_path)
        logger.debug(f"deleted file {file_path}")
        return True
    else:
        logger.warning(f"file does not exist to delete: {file_path}")
        return False


def random_string(length, use_punctuation=False, exclude=None):
    options = " " + string.ascii_letters
    if use_punctuation:
        options += string.punctuation
    if exclude:
        for c in exclude:
            options = options.replace(c, '')
    return ''.join([random.choice(options) for i in range(length)])


def random_hex_color():
    return "#" + ''.join([random.choice('ABCDEF0123456789') for i in range(6)])


# VALIDATIONS

def validate_note(note, expected):
    logger.info("Verify that the note has the correct data")
    logger.debug(f"note: {note}")
    logger.debug(f"expected: {expected}")
    for param in expected.keys():
        assert getattr(note, param) == expected[param]


def validate_config(expected):
    HOME_DIR = os.path.expanduser('~')
    SJOURNAL_DIR = os.path.join(HOME_DIR, 'sjournal')
    config_path = os.path.join(SJOURNAL_DIR, "sjournal_config.json")

    logger.info(f"Verify that the correct values are used in config: {config_path}")
    logger.debug(f"expected: {expected}")
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        logger.debug(f"config: {config}")
    for param in expected.keys():
        assert config[param] == expected[param]


def output_contains_note(output, note):
    logger.info(f"Searching for {note} in:\n{output}")
    regex = rf"{note.id}.*{note.timestamp}.*{note.category}.*{note.content[14:24]}"
    match = re.search(regex, output)
    if match:
        logger.debug(f"Found Note #{note.id} in output: {note}")
    else:
        logger.debug(f"Could not find Note # {note.id} in debug output\n{regex}")
    return match


def send_cli_command(commandline, assert_okay=True):
    logger.info(f"Sending command {commandline}")
    result = subprocess.run(commandline, shell=True, capture_output=False)
    logger.debug(result)
    if assert_okay:
        assert result.returncode == 0
    return result.returncode


def read_debug(debug_filename):
    logger.info(f"Reading debug file {debug_filename}")
    with open(debug_filename, "r") as output_file:
        full_text = output_file.read()
    logger.debug(f"\n{full_text}")
    return full_text
