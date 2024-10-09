from repository import GitRepository


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
