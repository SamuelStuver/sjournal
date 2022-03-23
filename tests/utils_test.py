import shutil
import os
import json
import random
import string
import subprocess
import re
from platform import system
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

def validate_note(note, expected_data):
    logger.info("Verify that the note has the correct data")
    logger.debug(f"note: {note}")
    logger.debug(f"expected data: {expected_data}")
    for param in expected_data.keys():
        assert getattr(note, param) == expected_data[param]


def validate_config(expected):
    HOME_DIR = os.path.expanduser('~')
    SJOURNAL_DIR = os.path.join(HOME_DIR, 'sjournal')
    config_path = os.path.join(SJOURNAL_DIR, "sjournal_config.json")

    logger.info(f"Confirm that the config file matches: {expected}")
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        logger.debug(f"config: {config}")
    for param in expected.keys():
        assert config[param] == expected[param]


def output_contains_note(output, note):
    # Maybe filter out newlines for the search?
    logger.info(f"Searching for [{note}] in output")

    regex = rf"{note.id}.*{note.timestamp}.*{note.category}.*{note.content[14:24]}".replace("\\", "\\\\")
    output_raw = output.replace('\n', '')

    match = re.search(regex, output_raw)
    if match:
        indices = match.span()
        match_text = output_raw[:indices[0]] + "[[[" + match.group(0) + "]]]" + output_raw[indices[1]:]
        logger.info(f"Found Note #{note.id} in output @ {indices}")
        logger.debug(match_text)
    else:
        logger.warning(f"Failed to find Note # {note.id} in debug output:")
        logger.warning(f"[{note}]")
        logger.warning(output_raw)

    return match


def output_contains_text(output, text):
    # Maybe filter out newlines for the search?
    logger.info(f'Searching for "{text}" in output')

    regex = rf"{text}".replace("\\", "\\\\")
    output_raw = output.replace('\n', '')
    match = re.search(regex, output_raw)
    logger.debug(output_raw)

    if match:
        indices = match.span()
        match_text = output_raw[:indices[0]] + "[[[" + match.group(0) + "]]]" + output_raw[indices[1]:]
        logger.info(f"Found text in output @ {indices}:")
        logger.debug(match_text)
    else:
        logger.warning(f'Failed to find "{text}" in output:')
        logger.warning(output_raw)

    return match


def send_cli_command(commandline, assert_okay=True, user_input=None):
    """
    Logging wrapper around the subprocess.run() function with simplified options
    :param commandline: string cli command to send
    :param assert_okay: If True, an error will be thrown if the command fails.
                         If False, the result will be returned and the code, stdout, and stderr can be used
                         All will be logged regardless
    :param user_input: String user input to capture and include in the process call
    :return: result: the CompletedProcess object including result code and stdout/stderr strings
    """

    logger.info(f"Sending command {commandline}")
    if system() == 'Linux':
        try:
            result = subprocess.run([commandline], check=assert_okay, input=user_input, shell=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as command_error:
            logger.info(f"RETURN CODE {command_error.returncode}")
            logger.debug(f"STDOUT: \n{command_error.stdout}")
            logger.debug(f"STDERR: \n{command_error.stderr}")
            raise command_error
    else:
        try:
            result = subprocess.run(commandline, check=assert_okay, input=user_input, shell=False, capture_output=True, text=True)
        except subprocess.CalledProcessError as command_error:
            logger.info(f"RETURN CODE {command_error.returncode}")
            logger.debug(f"STDOUT: \n{command_error.stdout}")
            logger.debug(f"STDERR: \n{command_error.stderr}")
            raise command_error

    logger.info(f"RETURN CODE {result.returncode} ({commandline})")
    logger.debug(f"STDOUT: \n{result.stdout}")
    logger.debug(f"STDERR: \n{result.stderr}")
    return result


def read_debug(debug_filename):
    logger.info(f"Reading debug file {debug_filename}")
    with open(debug_filename, "r") as output_file:
        full_text = output_file.read()
    logger.debug(f"\n{full_text}")
    return full_text