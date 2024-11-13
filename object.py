import collections
import hashlib
import os
import zlib

from repository import GitRepository, repo_file


class GitObject(object):
    """A git object abstraction"""

    def __init__(self, data=None) -> None:
        if data is not None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repo: GitRepository):
        """
        This function MUST be implemented by subclasses.

        It must read the object's contents from self.data, a byte string, and
        do whatever it takes to convert it into a meaningful representation.
        What exactly that means depend on each subclass.
        """
        raise NotImplementedError

    def deserialize(self, data):
        """Load an object from provided data"""
        raise NotImplementedError

    def init(self):
        pass


class GitCommit(GitObject):
    fmt = b"commit"

    def serialize(self, repo: GitRepository):
        return kvlm_serialize(self.kvlm)

    def deserialize(self, data: bytes):
        self.kvlm = kvlm_parse(data)

    def init(self):
        self.kvlm = collections.OrderedDict()


class GitTree(GitObject):
    fmt = b"tree"

    def serialize(self):
        return tree_serialize(self)

    def deserialize(self, data: bytes):
        self.items = tree_parse(data)

    def init(self):
        self.items = list()


class GitTreeLeaf(object):
    def __init__(self, mode: bytes, path: str, sha: str):
        self.mode = mode
        self.path = path
        self.sha = sha


class GitTag(GitObject):
    fmt = b"tag"


class GitBlob(GitObject):
    """A git blob object"""

    fmt = b"blob"

    def serialize(self):
        return self.blobdata

    def deserialize(self, data):
        self.blobdata = data


def object_read(repo: GitRepository, sha: str) -> GitObject | None:
    """
    Read object sha from the git repository.
    Return a GitObject subclass that depends on the object.
    """

    path = repo_file(repo, "objects", sha[:2], sha[2:])

    if not os.path.isfile(path):
        return None

    with open(path, "rb") as file:
        raw_object = zlib.decompress(file.read())

        # Read the object type
        space_index = raw_object.find(b" ")
        object_fmt = raw_object[:space_index]

        # Read and validate the object size
        null_index = raw_object.find(b"\x00", space_index)
        object_size = int(raw_object[space_index:null_index].decode("ascii"))
        if object_size != len(raw_object) - null_index - 1:
            raise Exception(f"Malformed object {sha}: bad length.")

        # Pick constructor
        match object_fmt:
            case b"commit":
                constructor = GitCommit
            case b"tree":
                constructor = GitTree
            case b"tag":
                constructor = GitTag
            case b"blob":
                constructor = GitBlob
            case _:
                raise Exception(
                    f"Unknown type {object_fmt.decode('ascii')} for object {sha}."
                )

        # Call constructor and return the object
        return constructor(raw_object[null_index + 1 :])


def object_write(obj: GitObject, repo: GitRepository | None = None) -> str:
    """
    Serialize the object and obtain its sha.
    If an existing repository is provided, object is writen to the repo.
    """

    # Serialize the object data
    data = obj.serialize()

    # Add header
    raw_object = obj.fmt + b" " + str(len(data)).encode() + b"\x00" + data

    # Compute hash
    sha = hashlib.sha1(raw_object).hexdigest()

    if repo:
        # Compute path
        path = repo_file(repo, "objects", sha[:2], sha[2:], mkdir=True)

        if not os.path.exists(path):
            with open(path, "wb") as file:
                # Compress and write
                file.write(zlib.compress(raw_object))

    return sha


def object_find(repo: GitRepository, name: str, fmt: bytes = None, follow: bool = True):
    """Temporary placeholder function for object name resolution."""
    return name


def object_hash(file_desc, fmt: bytes, repo: GitRepository | None = None) -> str:
    """Hash an object, writing it to a repository if provided"""
    data = file_desc.read()

    # Choose constructor depending on fmt argument
    match fmt:
        case b"commit":
            obj = GitCommit(data)
        case b"tree":
            obj = GitTree(data)
        case b"tag":
            obj = GitTag(data)
        case b"blob":
            obj = GitBlob(data)
        case _:
            raise Exception(f"Unknown type {fmt.decode()}.")

    return object_write(obj, repo)


def kvlm_parse(
    raw_object: bytes,
    start: int = 0,
    fields_dict: collections.OrderedDict | None = None,
) -> collections.OrderedDict:
    """Parse a Key-Value List with Message object into an OrderedDict."""
    if fields_dict is None:
        fields_dict = collections.OrderedDict()

    # This function is recursive, so we need to know if we are
    # at a keyword or already in the message.

    # We search for the next space and the next newline.
    next_space = raw_object.find(b" ", start)
    next_newline = raw_object.find(b"\n", start)

    # If space appears before newline, we found a keyword.
    # Otherwise, it's the final message, which we read until the end of the file.

    # Base case
    # =========
    # If newline appears first (or there's no space at all, in which
    # case find returns -1), we assume a blank line. A blank line
    # means the remainder of the data is the message. We store it in
    # the dictionary, with None as the key, and return.
    if next_space < 0 or next_newline < next_space:
        assert next_newline == start
        fields_dict[None] = raw_object[start + 1 :]
        return fields_dict

    # Recursive case
    # ==============
    # we read a key-value pair and recurse for the next.
    key = raw_object[start:next_space]

    # We loop until we find the end of the value, considering continuation lines
    # always begin with a space.
    end = start
    while end >= 0:
        end = raw_object.find(b"\n", end + 1)
        if raw_object[end + 1] != ord(" "):
            break

    # Get the value and drop leading space in continuation lines.
    value = raw_object[next_space + 1 : end].replace(b"\n ", b"\n")

    # Don't overwrite existing data contents
    if key in fields_dict:
        if type(fields_dict[key]) is list:
            fields_dict[key].append(value)
        else:
            fields_dict[key] = [fields_dict[key], value]
    else:
        fields_dict[key] = value

    return kvlm_parse(raw_object, start=end + 1, fields_dict=fields_dict)


def kvlm_serialize(fields_dict: collections.OrderedDict):
    """Serialize a Key-Value List with Message object from an OrderedDict"""
    output = b""

    # Add output fields
    for key in fields_dict.keys():
        # Skip the message
        if key is None:
            continue
        values = fields_dict[key]

        # Normalize to a list
        if type(values) is list:
            values = [values]

        for value in values:
            output += key + b" " + value.replace(b"\n", b"\n ") + b"\n"

    # Append message
    output += b"\n" + fields_dict[None] + b"\n"

    return output


def tree_parse_one(raw_object: bytes, start: int = 0) -> GitTreeLeaf:
    # Find the space terminator of the node
    space_term = raw_object.find(b" ", start)
    assert space_term - start == 5 or space_term - start == 6

    # Read the mode
    mode = raw_object[start:space_term]
    if len(mode) == 5:
        # Normalize to 6 bytes
        mode = b" " + mode

    # Find the NULL terminator of the path
    null_term = raw_object.find(b"\x00", space_term)
    # and read the path
    raw_path = raw_object[space_term + 1 : null_term]

    # Read the SHA
    raw_sha = int.from_bytes(raw_object[null_term + 1 : null_term + 21], "big")
    # and convert it into a zero-padded 40 chars hex string
    sha = format(raw_sha, "040x")

    return null_term + 21, GitTreeLeaf(mode, raw_path.decode(), sha)


def tree_parse(raw_object: bytes) -> list[GitTreeLeaf]:
    position = 0
    maximum = len(raw_object)
    output = list()

    while position < maximum:
        position, data = tree_parse_one(raw_object, position)
        output.append(data)

    return output


# Notice this isn't a comparison function, but a conversion function.
# Python's default sort doesn't accept a custom comparison function, like in most
# languages, but a `key` arguments that returns a new value, which is compared using
# the default rules.
# So we just return the leaf name, with an extra / if it's a directory.
def tree_leaf_sorting_key(leaf: GitTreeLeaf):
    if leaf.mode.startswith(b"10"):
        return leaf.path
    else:
        return leaf.path + "/"


def tree_serialize(tree: GitTree) -> bytes:
    tree.items.sort(key=tree_leaf_sorting_key)
    output = b""

    for item in tree.items:
        output += item.mode
        output += b" "
        output += item.path.encode()
        output += b"\x00"

        sha = int(item.sha, 16)
        output += sha.to_bytes(20, byteorder="big")

    return output
