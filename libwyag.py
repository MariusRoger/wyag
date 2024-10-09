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

argparser = argparse.ArgumentParser(description="My own git engine!")
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add":
            ...
        case _:
            ...
