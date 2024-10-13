import sys

from object import GitObject, object_find, object_hash, object_read
from repository import GitRepository, repo_create, repo_find


def cmd_add(args): ...
def cmd_cat_file(args):
    """CLI function to display contents of an object."""
    repo = repo_find()
    cat_file(repo, args.object, fmt=args.type.encode())


def cat_file(repo: GitRepository, obj: GitObject, fmt: bytes = None):
    """Displays the contents of an object"""
    out_obj = object_read(repo, object_find(repo, obj, fmt=fmt))
    sys.stdout.buffer.write(out_obj.serialize())


def cmd_check_ignore(args): ...
def cmd_checkout(args): ...
def cmd_commit(args): ...
def cmd_hash_object(args):
    if args.write:
        repo = repo_find()
    else:
        repo = None

    with open(args.path, "rb") as file_desc:
        sha = object_hash(file_desc, args.type.encode(), repo)
        print(sha)


def cmd_init(args):
    """CLI function to initialize a repository."""
    repo_create(args.path)


def cmd_log(args): ...
def cmd_ls_files(args): ...
def cmd_ls_tree(args): ...
def cmd_rev_parse(args): ...
def cmd_rm(args): ...
def cmd_show_ref(args): ...
def cmd_status(args): ...
def cmd_tag(args): ...
