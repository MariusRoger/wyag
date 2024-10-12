import collections
import grp
import pwd
import re
import sys
from datetime import datetime
from fnmatch import fnmatch
from math import ceil

import cli_commands as commands
from cli_parser import argparser


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add":
            commands.cmd_add(args)
        case "cat-file":
            commands.cmd_cat_file(args)
        case "check-ignore":
            commands.cmd_check_ignore(args)
        case "checkout":
            commands.cmd_checkout(args)
        case "commit":
            commands.cmd_commit(args)
        case "hash-object":
            commands.cmd_hash_object(args)
        case "init":
            commands.cmd_init(args)
        case "log":
            commands.cmd_log(args)
        case "ls-files":
            commands.cmd_ls_files(args)
        case "ls-tree":
            commands.cmd_ls_tree(args)
        case "rev-parse":
            commands.cmd_rev_parse(args)
        case "rm":
            commands.cmd_rm(args)
        case "show-ref":
            commands.cmd_show_ref(args)
        case "status":
            commands.cmd_status(args)
        case "tag":
            commands.cmd_tag(args)
        case _:
            print("Bad command.")
