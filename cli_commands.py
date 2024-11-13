import os
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
    """CLI function to hash an object and possibly store it in the repository."""
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


def cmd_log(args):
    """CLI function to display commit history as graphviz data."""
    repo = repo_find()

    print("digraph wyaglog{")
    print("  node[shape=rect]")
    log_graphviz(repo, object_find(repo, args.commit), set())
    print("}")


def log_graphviz(repo: GitRepository, sha: str, already_seen: set):
    """Recursively print the graphviz representation of the history from a commit"""
    if sha in already_seen:
        return
    already_seen.add(sha)

    commit = object_read(repo, sha)
    short_hash = sha[:8]
    message = commit.kvlm[None].decode().strip()
    message = message.replace("\\", "\\\\")
    message = message.replace('"', '\\"')

    # Keep only the first line.
    if "\n" in message:
        message = message[: message.index("\n")]

    print(f'  c_{sha} [label="{short_hash}: {message}"]')
    assert commit.fmt == b"commit"

    # Base case : initial commit
    if b"parent" not in commit.kvlm.keys():
        return

    parents = commit.kvlm[b"parent"]

    if type(parents) is not list:
        parents = [parents]

    for parent in parents:
        parent = parent.decode("ascii")
        print(f"  c_{sha} -> c_{parent};")
        log_graphviz(repo, parent, already_seen)


def cmd_ls_files(args): ...
def cmd_ls_tree(args):
    repo = repo_find()
    ls_tree(repo, args.tree, args.recursive)


def ls_tree(repo: GitRepository, ref: str, recursive: bool = None, prefix: str = ""):
    sha = object_find(repo, ref, fmt=b"tree")
    obj = object_read(repo, sha)

    for item in obj.items:
        if len(item.mode) == 5:
            item_raw_type = item.mode[:1]
        else:
            item_raw_type = item.mode[:2]

        match item_raw_type:
            case b"04":
                item_type = "tree"
            case b"10":
                item_type = "blob"  # A regular file
            case b"12":
                item_type = "blob"  # A symlink. Blob contents is link target
            case b"16":
                item_type = "commit"  # A submodule
            case _:
                raise Exception(f"Unknown tree leaf mode {item_raw_type}")
        
        # If this is a leaf
        if not (recursive and item_type=='tree'):
            print(f"{"0"* (6-len(item.mode)) + item.mode.decode("ascii")} "
                  + f"{item_type} {item.sha}\t{os.path.join(prefix, item.path)}")
        
        else:
            ls_tree(repo, item.sha, recursive, os.path.join(prefix, item.path))


def cmd_rev_parse(args): ...
def cmd_rm(args): ...
def cmd_show_ref(args): ...
def cmd_status(args): ...
def cmd_tag(args): ...
