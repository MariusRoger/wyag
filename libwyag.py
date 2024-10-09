import argparse
import collections
import configparser
import grp
import hashlib
import os
import pwd
import re
import sys
import zlib
from datetime import datetime
from fnmatch import fnmatch
from math import ceil

from repository import repo_create

argparser = argparse.ArgumentParser(description="My own git engine!")
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True


argsp = argsubparsers.add_parser("init", help="Initialize a new (empty) repository.")
argsp.add_argument(
    "path",
    metavar="directory",
    nargs="?",
    default=".",
    help="Where to create the repository.",
)


def cmd_add(args): ...
def cmd_cat_file(args): ...
def cmd_check_ignore(args): ...
def cmd_checkout(args): ...
def cmd_commit(args): ...
def cmd_hash_object(args): ...
def cmd_init(args):
    repo_create(args.path)


def cmd_log(args): ...
def cmd_ls_files(args): ...
def cmd_ls_tree(args): ...
def cmd_rev_parse(args): ...
def cmd_rm(args): ...
def cmd_show_ref(args): ...
def cmd_status(args): ...
def cmd_tag(args): ...


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add":
            cmd_add(args)
        case "cat-file":
            cmd_cat_file(args)
        case "check-ignore":
            cmd_check_ignore(args)
        case "checkout":
            cmd_checkout(args)
        case "commit":
            cmd_commit(args)
        case "hash-object":
            cmd_hash_object(args)
        case "init":
            cmd_init(args)
        case "log":
            cmd_log(args)
        case "ls-files":
            cmd_ls_files(args)
        case "ls-tree":
            cmd_ls_tree(args)
        case "rev-parse":
            cmd_rev_parse(args)
        case "rm":
            cmd_rm(args)
        case "show-ref":
            cmd_show_ref(args)
        case "status":
            cmd_status(args)
        case "tag":
            cmd_tag(args)
        case _:
            print("Bad command.")
