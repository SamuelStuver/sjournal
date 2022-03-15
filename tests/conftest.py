import pytest
import os
from utils_test import get_project_root


def pytest_addoption(parser):
    parser.addoption("--test_environment", action="store", default="local_repo", choices=["local_repo", "jenkins_repo", "local_publish", "remote_publish"])


@pytest.fixture(scope='session')
def environment(request):
    ROOT_DIR = get_project_root()
    HOME_DIR = os.path.expanduser('~')
    SJOURNAL_DIR = os.path.join(HOME_DIR, 'sjournal')
    DEBUG_OUTPUT = os.path.join(SJOURNAL_DIR, "reports", "debug.log")

    env = request.config.option.test_environment
    if env == "local_repo":
        sjournal_exec = f"python {os.path.join(ROOT_DIR, 'run.py')}"
    elif env == "jenkins_repo":
        sjournal_exec = f"python {os.path.join(ROOT_DIR, 'run.py')}"
    elif env == "local_publish" or env == "remote_publish":
        sjournal_exec = "sjournal"
    else:
        sjournal_exec = "sjournal"

    return ROOT_DIR, HOME_DIR, SJOURNAL_DIR, DEBUG_OUTPUT, sjournal_exec