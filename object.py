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


class GitTree(GitObject):
    fmt = b"tree"


class GitTag(GitObject):
    fmt = b"tag"


class GitBlob(GitObject):
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
