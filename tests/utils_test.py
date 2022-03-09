import shutil
import os


def get_project_root():
    return os.path.abspath(os.curdir)


def backup_file(file_path, new_path=None):
    ext = os.path.splitext(file_path)[1]
    if not new_path:
        new_path = f"{os.path.splitext(file_path)[0]}_backup{ext}"

    shutil.copyfile(file_path, new_path)
    return new_path


def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        return True
    else:
        return False


if __name__ == "__main__":
    #backup_file(r"C:\Users\samue\Projects\sjournal\config.json")
    delete_file(r"C:\Users\samue\Projects\sjournal\config_backup.json")