# -*- coding: utf-8 -*-
import os
import setuptools
import json
from version_utils import get_package_version

# ======================================================================================================================
# Fill in this information for each package.
# ======================================================================================================================

CONFIG_FILE = "build_config.json"

# Load Config.
with open(CONFIG_FILE, "r") as config_file:
    config = json.load(config_file)

AUTHOR = config["author"]
EMAIL = config["email"]
DESCRIPTION = config["description"]
REPO = config["url"]
SCRIPTS = config["scripts"]
PYTHON_VERSION = config["python_version"]
PACKAGE_SRC = "../src"
PACKAGE_NAME_OVERRIDE = (
    None
    if "package_name_override" not in config or config["package_name_override"] is None
    else config["package_name_override"]
)

CLASSIFIERS = ["License :: OSI Approved :: MIT License",
               "Operating System :: Microsoft :: Windows :: Windows 10",
               "Operating System :: POSIX :: Linux"]

for py_ver in PYTHON_VERSION:
    CLASSIFIERS.append(f"Programming Language :: Python :: {py_ver}")

# ======================================================================================================================
# Discover the core package.
# ======================================================================================================================

# Work out the sources package.
src_paths = os.listdir(PACKAGE_SRC)
src_to_remove = [
    "__pycache__",
    "__init__.py",
    ".pytest_cache",
]

# Make sure we don't include this by accident.
for src_element in src_to_remove:
    if src_element in src_paths:
        src_paths.remove(src_element)

if len(src_paths) != 1:
    raise Exception(
        f"Failed to build: Source directory '{PACKAGE_SRC}' must contain exactly one Python package. "
        f"Instead, it contains {len(src_paths)}: {src_paths}"
    )

PACKAGE_NAME = src_paths[0]
PACKAGE_PATH = os.path.join(PACKAGE_SRC, PACKAGE_NAME)
print(f"Package Name Discovered: {PACKAGE_NAME}")
if PACKAGE_NAME_OVERRIDE is None:
    PACKAGE_NAME_OVERRIDE = PACKAGE_NAME


# ======================================================================================================================
# Automatic Package Setup Script.
# ======================================================================================================================

final_version = str(get_package_version())

# Copy the README into the long description.
with open("../README.md", "r") as f:
    long_description = f.read()

packages = setuptools.find_packages(PACKAGE_SRC)
print(f"Packages Discovered: {packages}")

REQUIREMENTS_FILE = "../requirements.txt"
if os.path.exists(REQUIREMENTS_FILE):
    with open(REQUIREMENTS_FILE, "r") as f:
        requirement_packages = [line.strip("\n") for line in f.readlines()]
    print(f"Requirements: {requirement_packages}")
else:
    print(f"Requirements file not found at {REQUIREMENTS_FILE}")
    requirement_packages = []



setuptools.setup(
    author=AUTHOR,
    author_email=EMAIL,
    name=PACKAGE_NAME_OVERRIDE,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=str(final_version),
    url=REPO,
    packages=packages,
    package_dir={PACKAGE_NAME: PACKAGE_PATH},
    install_requires=requirement_packages,
    classifiers=CLASSIFIERS,
    entry_points={"console_scripts": SCRIPTS},
)
