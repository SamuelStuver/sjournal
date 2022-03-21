import json
import os
import semver
import subprocess
import argparse
import requests
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--increment', action='store', default=None, choices=["major", "minor", "patch", "prerelease", None],
                        help="Increment the major, minor, patch, or prerelease version")

    parser.add_argument('-s', '--set', action='store', default=None, help="Set a specific version")

    parser.add_argument('-v', '--version', action='store_true', help="Show the current version")
    parser.add_argument('-l', '--location', action='store', default="local", choices=["local", "remote"],
                        help="Show the current version")
    parser.add_argument('-t', '--use_tag', action='store_true',
                        help="Use the tag for the current commit to update the version")
    parser.add_argument('-f', '--force', action='store_true', help="force publish without verifying version or branch")
    return parser.parse_args()


def get_current_commit_sha():
    command = "git rev-parse HEAD".split()
    resp = subprocess.check_output(command)
    commit_sha = resp.decode("utf-8").strip()
    return commit_sha


def get_source_branch(commit_sha):
    command = f"git name-rev --name-only --exclude=tags/* {commit_sha}".split()
    resp = subprocess.check_output(command)
    branch_name = resp.decode("utf-8").strip()
    return branch_name


def get_git_tag():
    command = "git describe --tags --abbrev=0 --exact-match".split()
    print("\nAttempting to get tag from latest commit...")
    try:
        resp = subprocess.check_output(command)
        tag_name = resp.decode("utf-8").strip()
    except subprocess.CalledProcessError:
        print(f"Failed to get tag for current commit.\n")
        return None

    return tag_name


def get_pypi_version():
    url = 'https://pypi.python.org/pypi/sjournal/json'
    print(f"\nGetting current published version from {url}")
    result = requests.get(url).json()
    pypi_version = result['info']['version']

    print(f"Retrieved version {pypi_version} from PyPI")
    return semver.VersionInfo.parse(pypi_version)


def get_package_version():
    version_path = os.path.join(ROOT_DIR, "src", "sjournal", "utilities", "version.py")

    with open(version_path, "r") as version_file:
        version_line = version_file.readline()

    regex = r'__version__ = \"(.*)\"'
    version = re.search(regex, version_line).group(1)

    return semver.VersionInfo.parse(version)


def copy_version_to_package(version):

    version_path = os.path.join(ROOT_DIR, "src", "sjournal", "utilities", "version.py")

    with open(version_path, "w") as version_file:
        version_file.write(f'__version__ = "{version}"\n')


def increment_version(current_version, part):

    # Get the current version
    new_version = current_version

    # Increment the version
    new_version = new_version.next_version(part, prerelease_token="alpha")

    # Return new version.
    print(f"Bumped Version Number to {new_version}")
    return new_version


def set_version(version_string):

    version_is_valid = semver.VersionInfo.isvalid(version_string)
    if version_is_valid:
        new_version = semver.VersionInfo.parse(version_string)

        print(f"Set Version Number to {new_version}")
        return new_version
    else:
        if not version_is_valid:
            print(f"{version_string} is not a valid SemVer value.")
            exit(1)


def handle_version(args):
    print(args)
    pypi_version = get_pypi_version()
    final_version = pypi_version

    if args.version:
        print(f"Current Version: {str(final_version)}")

    elif args.use_tag:
        tag_name = get_git_tag()
        if tag_name is not None:
            tag_is_version = semver.VersionInfo.isvalid(tag_name.strip("v"))
            tag_is_increment = tag_name in ['major', 'minor', 'patch', 'prerelease']

            print(f"Using Tag: {tag_name} - Is Increment: {tag_is_increment} - Is Version: {tag_is_version}")

            if tag_is_version:
                final_version = set_version(tag_name.strip("v"))
            elif tag_is_increment:
                final_version = increment_version(pypi_version, tag_name)

    elif args.set:
        final_version = set_version(args.set)

    elif args.increment:
        final_version = increment_version(pypi_version, args.increment)

    print(f"\nPrevious Version: {str(pypi_version)}\nCurrent Version: {str(final_version)}\n")
    print(f"Copying new version to the package")
    copy_version_to_package(str(final_version))
    print("Done.\n")

    return pypi_version, final_version


if __name__ == "__main__":
    args = parse_arguments()
    print(ROOT_DIR)
    current_commit = get_current_commit_sha()
    source_branch = get_source_branch(current_commit)

    branch_can_publish = (source_branch == "main") or ("remotes/origin/main" in source_branch)

    prev_version, final_version = handle_version(args)

    assert final_version == str(get_package_version())

    if args.location == "remote":
        if not args.force:
            assert branch_can_publish, f"Attempted to publish remote from non-main branch ({source_branch} - {current_commit}).\nCheckout 'main' and merge changes before publishing."
            assert final_version > prev_version, f"Attempted to publish remote without incrementing the version ({str(prev_version)} -> {str(final_version)}).\nIncrease the version first."
        else:
            if not branch_can_publish:
                print(f"BYPASS - publish remote from non-main branch ({source_branch}).")
            if final_version <= prev_version:
                print(f"BYPASS - publish remote without incrementing the version ({str(prev_version)} -> {str(final_version)})")
        print()