# sjournal ![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/SamuelStuver/sjournal?include_prereleases&logo=github)
A simple and light-weight notepad for the command line:

![Demo](/demo.png)

## Installation
### via pip
```bash
> git clone https://github.com/SamuelStuver/sjournal.git
> cd sjournal
> pip install -r requirements.txt --user
```
### via pipenv
```bash
> git clone https://github.com/SamuelStuver/sjournal.git
> cd sjournal
> pipenv shell
> pipenv install
```

## Set up [Cmder](https://cmder.net) alias 
In the step blow, replace `sjournal=` with the name for the alias you want to run sjournal with:
```bash
> echo sjournal=python <PATH TO REPO>\sjournal.py $* >> %CMDER_ROOT%\config\user_aliases.cmd
```
Then, sjournal can be run via alias in the command line:
```bash
> sjournal
```

## Set up Windows Cmd alias
In the steps below, replace `sjournal` in `sjournal.bat` with the name for the alias you want to run sjournal with:
```bash
> cd c:/
> mkdir alias
> cd alias
> echo @echo off >> sjournal.bat
> echo echo. >> sjournal.bat
> echo python <PATH TO REPO>\sjournal.py %* >> sjournal.bat
```
Finally, add `c:/alias` to PATH in your system environment variables.
Then, sjournal can be run via alias in the command line:
```bash
> sjournal
```

## Usage
```
usage: sjournal.py [-h] {add,backup,categories,delete,edit,erase,help,list,load,restore,search} ...

options:
  -h, --help            show this help message and exit

Commands:
  {add,backup,categories,delete,edit,erase,help,list,load,restore,search}
                        Commands
    add                 Add a note to the database
    backup              Backup the current journal
    categories          List all categories in the current journal
    delete              Delete one or multiple notes from the database
    edit                Edit a note to the database
    erase               Delete all notes from the database
    help                Display help text
    list                List notes in the database
    load                Load a journal or create a new one if it doesn't exist
    restore             Restore the database from a file. If --filename is not given, restore the latest backup
    search              List notes matching search term

 To see help for specific commands, use sjournal.py [COMMAND] --help
```
