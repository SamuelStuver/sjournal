import os
import re


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