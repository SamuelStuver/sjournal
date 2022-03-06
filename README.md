# sjournal
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
