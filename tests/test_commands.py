import pytest
import logging
import subprocess
from sjournal import SJournal, Note
from utils_test import backup_file, delete_file, get_project_root
import argparse
import os

# Suite of tests to validate the CLI interface for sjournal using subprocess to call the application


@pytest.fixture(scope="function")
def clean_journal_fixture():
    logging.info("START OF TEST")
    # backup current config file
    ROOT_DIR = get_project_root()
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


def test_load(clean_journal_fixture):
    journal = clean_journal_fixture
    pytest.xfail("TODO")


def test_add_note(clean_journal_fixture):
    journal = clean_journal_fixture
    pytest.xfail("TODO")


def test_edit_note():
    pytest.xfail("TODO")


def test_delete_note():
    pytest.xfail("TODO")


def test_list():
    pytest.xfail("TODO")


def test_categories():
    pytest.xfail("TODO")


def test_backup():
    pytest.xfail("TODO")


def test_restore():
    pytest.xfail("TODO")


def test_erase():
    pytest.xfail("TODO")


def test_search():
    pytest.xfail("TODO")


def test_help():
    pytest.xfail("TODO")