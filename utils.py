import os
import re
import subprocess

def count_backups(dir):
    db_file_list = os.listdir(dir)
    count = 0
    for f in db_file_list:
        if re.search(r"notes_backup_.*", f) is not None:
            count += 1
    return count


def get_newest_file(dir):
    try:
        db_file_list = os.listdir(dir)
    except FileNotFoundError:
        return None
    for i, filename in enumerate(db_file_list):
        db_file_list[i] = os.path.join(dir, filename)
    return max(db_file_list, key=os.path.getctime)


def range_parser(item_list):
    regex = r"(\d*)\W(\d*)"
    new_list = []
    for item in item_list:
        if item.isnumeric():
            new_list.append(int(item))
        else:
            match = re.search(regex, item)
            if match:
                minimum, maximum = match.groups()
                if minimum.isnumeric() and maximum.isnumeric():
                    for i in range(int(minimum), int(maximum) + 1):
                        new_list.append(int(i))
                else:
                    new_list.append(item)
    return new_list


def copy_to_clipboard(txt):
    cmd = f'echo {txt.strip()} |clip'
    return subprocess.check_call(cmd, shell=True)