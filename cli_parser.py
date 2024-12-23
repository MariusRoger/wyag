import argparse

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


argsp = argsubparsers.add_parser(
    "cat-file", help="Provide content of a repository object."
)
argsp.add_argument(
    "type",
    metavar="type",
    choices=["blob", "commit", "tag", "tree"],
    help="Specify the type.",
)
argsp.add_argument(
    "object",
    metavar="object",
    help="The object to display.",
)


argsp = argsubparsers.add_parser(
    "hash-object", help="Compute object ID and optionally creates a blob from a file."
)
argsp.add_argument(
    "-t",
    metavar="type",
    dest="type",
    choices=["blob", "commit", "tag", "tree"],
    default="blob",
    help="Specify the type.",
)
argsp.add_argument(
    "-w",
    dest="write",
    action="store_true",
    help="Actually write the object into the database.",
)
argsp.add_argument(
    "path",
    help="Read object from <file>.",
)


argsp = argsubparsers.add_parser("log", help="Display commit history.")
argsp.add_argument(
    "commit",
    default="HEAD",
    nargs="?",
    help="Commit to start at.",
)


argsp = argsubparsers.add_parser("ls-tree", help="Pretty-print a tree object.")
argsp.add_argument(
    "-r",
    dest="recursive",
    action="store_true",
    help="Recurse into sub-trees.",
)
argsp.add_argument(
    "tree",
    help="A tree-like object.",
)
