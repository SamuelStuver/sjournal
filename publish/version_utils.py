import json
import os
import sys
import semver
import subprocess
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--increment', action='store', default=None, choices=["major", "minor", "patch", "prerelease", None],
                        help="Increment the major, minor, patch, or prerelease version")

    parser.add_argument('-s', '--set', action='store', default=None, help="Set a specific version")

    parser.add_argument('-v', '--version', action='store_true', help="Show the current version")

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


def increment_version(part):

    # Get the current version
    current_version = get_current_version()
    new_version = current_version

    # Increment the version
    if get_git_branch() != "main":
        # CONFIRM THAT INCREASING THE VERSION IS OKAY OUTSIDE OF MAIN
        pass
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

    if semver.VersionInfo.isvalid(version_string):
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
        print(f"{version_string} is not a valid SemVer value.")
        exit(1)


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


if __name__ == "__main__":
    args = parse_arguments()
    if args.version:
        print(f"Current Version: {str(get_current_version())}")
    if args.set:
        set_version(args.set)
    elif args.increment:
        increment_version(args.increment)
