import argparse


def parse_args():

    # Read environment from command line args
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', help='Commands', title='Commands')

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a note to the database')
    parser_add.add_argument('content', nargs='*', action='store', type=str, default=None,
                            help="Content of note")
    parser_add.add_argument('-c', '--category', default='General', action='store',
                            help="Choose a category for the note to be added under")
    parser_add.add_argument('-s', '--style', default=None, action='store',
                            help="Specify a rich console markup style to the note for display")

    # Edit command
    parser_edit = subparsers.add_parser('edit', help='Edit a note to the database')
    parser_edit.add_argument('id', nargs='?', action='store', type=int, default=None,
                             help="ID of note to edit")

    # List command
    parser_list = subparsers.add_parser('list', help='List notes in the database')
    parser_list.add_argument('quantity', nargs='*', action='store', default=5, type=int,
                             help="Specify the amount of results to list")

    parser_list.add_argument('-a', '--all', action='store_true',
                             help="List all notes under given criteria")

    parser_list.add_argument('-c', '--category', nargs='?', default=None, action='store',
                             help="Choose a category of notes to list")
    parser_list.add_argument('-r', '--reverse', action='store_true',
                             help="Display notes in reverse chronological order")

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete one or multiple notes from the database')
    parser_delete.add_argument('delete_criteria', nargs='*', action='store', type=str)

    # Erase command
    parser_erase = subparsers.add_parser('erase', help='Delete all notes from the database')

    # Backup command
    parser_backup = subparsers.add_parser('backup', help='Backup the database. 10 backups are stored at a time')
    parser_backup.add_argument('-f', '--filename', action='store', default=None,
                               help='Choose a filename to use for the backup file. By default, the current timestamp will be used')

    # Restore command
    parser_restore = subparsers.add_parser('restore', help='Restore the database from a file. If --filename is not given, restore the latest backup')
    parser_restore.add_argument('-f', '--filename', action='store', default=None,
                               help='Specify a file to backup data from. If not specified, the latest backup file will be used')

    # Help command
    parser_help = subparsers.add_parser('help', help='Display help text')
    parser_help.add_argument('help_command', nargs='?', action='store', default=None)

    # Search command
    parser_search = subparsers.add_parser('search', help='List notes matching search term')
    parser_search.add_argument('search_criteria', nargs='+', action='store', type=str)

    # Load command
    parser_load = subparsers.add_parser('load', help="Load a journal or create a new one if it doesn't exist")
    parser_load.add_argument('journal_name', action='store', type=str)

    # Categories command
    parser_categories = subparsers.add_parser('categories', help="List all categories in the current journal")
    parser_categories.add_argument('search_criteria', nargs="?", action='store', type=str)

    args = parser.parse_args()
    parsers = {
        'add':parser_add,
        'edit':parser_edit,
        'list':parser_list,
        'delete':parser_delete,
        'erase':parser_erase,
        'backup':parser_backup,
        'restore':parser_restore,
        'search':parser_search,
        'load':parser_load,
        'categories': parser_categories,
        'help':parser_help
    }

    if args.command == "help":
        if not args.help_command or args.help_command not in parsers.keys():
            parser.print_help()
        else:
            parsers[args.help_command].print_help()
        exit()

    return args