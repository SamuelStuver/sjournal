import json
import os
import sys
import semver
import subprocess
import argparse
from rich.prompt import Confirm


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


def get_git_branch():
    command = "git rev-parse --abbrev-ref HEAD".split()
    resp = subprocess.check_output(command)
    branch_name = resp.decode("utf-8").strip()
    return branch_name


def get_current_version():
    # Read version from config file
    with open("build_config.json", "r") as f:
        config_object = json.load(f)
        version = semver.VersionInfo.parse(config_object["version"])

    return version


def get_git_tag():
    command = "git describe --tags --abbrev=0 --exact-match".split()
    try:
        resp = subprocess.check_output(command)
        tag_name = resp.decode("utf-8").strip()
    except subprocess.CalledProcessError:
        print(f"Failed to get tag for current commit. Make sure the commit is tagged.")
        return None

    return tag_name


def increment_version(part):

    # Get the current version
    current_version = get_current_version()
    new_version = current_version

    # Increment the version. If branch is not main, ask for confirmation first
    new_version = new_version.next_version(part, prerelease_token="alpha")

    # Update the config file with the new version
    with open("build_config.json", "r") as confile:
        config = json.load(confile)
    with open("build_config.json", "w") as confile:
        config["version"] = str(new_version)
        json.dump(config, confile, indent=2)

    # Return new version.
    print(f"Bumped Version Number: {current_version} -> {new_version}")
    return new_version


def set_version(version_string):
    current_version = get_current_version()

    version_is_valid = semver.VersionInfo.isvalid(version_string)
    if version_is_valid:
        new_version = semver.VersionInfo.parse(version_string)

        # Update the config file with the new version
        with open("build_config.json", "r") as confile:
            config = json.load(confile)
        with open("build_config.json", "w") as confile:
            config["version"] = str(new_version)
            json.dump(config, confile, indent=2)
        print(f"Set Version Number: {current_version} -> {new_version}")
        return new_version
    else:
        if not version_is_valid:
            print(f"{version_string} is not a valid SemVer value.")
        return current_version


# Copy the version to the __init__.py file.
def copy_version_to_package(path, version):
    """ Copy the single source of truth version number into the package as well. """

    # Copy __version__ to all root-level files in path.
    copy_files = ["utilities/version.py"]

    for file_name in copy_files:
        target_file = os.path.join(path, file_name)
        with open(target_file, "r") as original_file:
            lines = original_file.readlines()

        with open(target_file, "w") as new_file:
            for line in lines:
                if "__version__" not in line:
                    new_file.write(line)
                else:
                    new_file.write('__version__ = "{}"\n'.format(version))


def handle_version(args):
    print(args)
    original_version = get_current_version()
    final_version = original_version
    tag_name = get_git_tag()

    if args.version:
        print(f"Current Version: {str(final_version)}")

    elif args.use_tag:
        if tag_name is not None:
            tag_is_version = semver.VersionInfo.isvalid(tag_name)
            tag_is_increment = tag_name in ['major', 'minor', 'patch', 'prerelease']

            print(f"Using Tag: {tag_name} - Is Increment: {tag_is_increment} - Is Version: {tag_is_version}")

            if tag_is_version:
                final_version = set_version(tag_name)
            elif tag_is_increment:
                final_version = increment_version(tag_name)

    elif args.set:
        final_version = set_version(args.set)

    elif args.increment:
        final_version = increment_version(args.increment)

    print(f"\nPrevious Version: {str(original_version)}\nCurrent Version: {str(final_version)}\n")

    return final_version


if __name__ == "__main__":
    args = parse_arguments()
    prev_version = get_current_version()

    current_branch = get_git_branch()

    if args.location == "remote":
        final_version = handle_version(args)

        if not args.force:
            assert current_branch == "main", f"Attempted to publish remote from non-main branch ({current_branch}).\nCheckout 'main' and merge changes before publishing."
            assert final_version > prev_version, f"Attempted to publish remote without incrementing the version ({str(prev_version)} -> {str(final_version)}).\nIncrease the version first."
        else:
            if current_branch != "main":
                print(f"BYPASS - publish remote from non-main branch ({current_branch}).")
            if final_version <= prev_version:
                print(f"BYPASS - publish remote without incrementing the version ({str(prev_version)} -> {str(final_version)})")