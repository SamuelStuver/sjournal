# sjournal ![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/SamuelStuver/sjournal?include_prereleases&logo=github)
A simple and light-weight notepad for the command line:

![Demo](https://raw.githubusercontent.com/SamuelStuver/sjournal/main/demo.png)
![Demo](./demos/demo.png)

## Installation
### Latest release via pip
```bash
> pip install sjournal
```

## Usage
Sjournal commands can be invoked using either `sjournal` or `sj`
### Creating and Loading Journals
If using Sjournal for the first time, a blank journal called "notes" will be automatically created:
```bash
> sjournal

No config file found. Creating new one at <HOME_DIR>/sjournal/sjournal_config.json

                 notes
┌────┬───────────┬──────────┬─────────┐
│ ID │ Timestamp │ Category │ Content │
├────┼───────────┼──────────┼─────────┤
└────┴───────────┴──────────┴─────────┘
```

To create a new Journal or load an Existing one, use `sjournal load`:
```bash
> sjournal load MyJournal
Set journal to <HOME_DIR>/sjournal/journals/MyJournal.db

> sjournal

               MyJournal
┌────┬───────────┬──────────┬─────────┐
│ ID │ Timestamp │ Category │ Content │
├────┼───────────┼──────────┼─────────┤
└────┴───────────┴──────────┴─────────┘
```

### Adding, Editing, Deleting Notes
Add notes with `sjournal add` 

- Set the category with `-c/--category`. Default category is "General"
- Set the Style ([Rich Markup](https://rich.readthedocs.io/en/latest/markup.html)) with `-s/--style`
![Demo](demos/add_note.png)


## Setting up [Cmder](https://cmder.net) alias 
If you want to run Sjournal with a different shorthand within Cmder (such as `myalias`):
```bash
> alias myalias=sjournal $*
```
After restarting Cmder, sjournal can be used by calling the new alias in the command line:
```bash
> myalias --version
```

## Setting up Windows Cmd alias
If you want to run Sjournal with a different shorthand within Windows Cmd (such as `myalias`):
```bash
> cd c:/
> mkdir alias
> cd alias
> echo @echo off >> myalias.bat
> echo echo. >> myalias.bat
> echo sjournal %* >> myalias.bat
```
Finally, add `c:/alias` to PATH in your system environment variables.

After restarting Cmd, sjournal can be used by calling the new alias in the command line:
```bash
> myalias --version
```

## Full List of Commands
To see help for a specific command, use `sjournal [COMMAND] --help`
```
usage: sjournal [-h] [-d] [-v] {add,backup,categories,delete,edit,erase,help,list,load,restore,search} ...

options:
  -h, --help            show this help message and exit
  -d, --debug           Output to reports/debug.log instead of stdout
  -v, --version         Show sjournal information

Commands:
  {add,backup,categories,delete,edit,erase,help,list,load,restore,search}
                        Commands
    add                 Add a note to the database
    backup              Backup the current journal
    categories          List all categories in the current journal
    delete              Delete one or multiple notes from the database
    edit                Edit a note to the database
    erase               Delete all notes from the current journal
    help                Display help text
    list                List notes in the database
    load                Load a journal or create a new one if it doesn't exist
    restore             Restore the database from a file. If --filename is not given, restore the latest backup
    search              List notes matching search term

 
```
To see help for specific commands, use sjournal [COMMAND] --help
