import configparser
import os
from pathlib import Path


class GitRepository(object):
    """A git repository"""

    worktree = None
    gitdir = None
    conf_parser = None

    def __init__(self, path: str | Path, force: bool = False) -> None:
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"Not a Git repository : {path}")

        # Read configuration file in .git/config
        self.conf_parser = configparser.ConfigParser()
        config_file = repo_file(self, "config")

        if config_file and os.path.exists(config_file):
            self.conf_parser.read([config_file])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            version = int(self.conf_parser.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception(f"Unsupported repositoryformatversion {version}")


def repo_path(repo: GitRepository, *path: str | Path) -> str:
    """Compute path under repo's gitdir."""
    return os.path.join(repo.gitdir, *path)


def repo_file(
    repo: GitRepository, *path: str | Path, mkdir: bool = False
) -> str | None:
    """
    Compute path under repo's gitdir, and create dirname(*path) if absent.

    For example, repo_file(r, "refs", "remotes", "origin", "HEAD") will create
    .git/refs/remotes/origin.
    """
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)
    return None


def repo_dir(repo: GitRepository, *path: str | Path, mkdir: bool = False) -> str | None:
    """Compute path under repo's gitdir, and mkdir *path if absent and mkdir"""
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    return None


def repo_create(path: str | Path) -> GitRepository:
    """Create a new git repository at path"""
    # Make sure we are not already in a repository
    existing_repo = repo_find(path, required=False)
    if existing_repo and (existing_repo.worktree != os.path.realpath(path)):
        raise Exception(
            f"Cannot create repository within a repository, located at {existing_repo.worktree}."
        )

    repo = GitRepository(path, force=True)

    # Make sure the path either doesn't exist or is an empty dir
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception(f"{path} is not a directory.")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"{path} is not empty.")
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # .git/description
    with open(repo_file(repo, "description"), "w") as file:
        file.write("Unnamed repository; edit this file to name the repository.\n")

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as file:
        file.write("ref: refs/heads/master\n")

    # .git/config
    with open(repo_file(repo, "config"), "w") as file:
        config = repo_default_config()
        config.write(file)

    return repo


def repo_default_config() -> configparser.ConfigParser:
    """Create the default configuration"""
    config = configparser.ConfigParser()

    config.add_section("core")
    config.set("core", "repositoryformatversion", "0")
    config.set("core", "filemode", "false")
    config.set("core", "bare", "false")

    return config


def repo_find(path: str | Path = ".", required: bool = True) -> GitRepository | None:
    real_path = os.path.realpath(path)

    if os.path.isdir(os.path.join(real_path, ".git")):
        return GitRepository(real_path)

    # If there is no .git file, recurse in parent
    parent = os.path.realpath(os.path.join(real_path, ".."))

    if parent == path:
        # Base case : os.path.join("/", "..") == "/":
        # If parent==path, then path is root.
        if required:
            raise Exception("Not a git directory.")
        else:
            return None

    # Recursion step
    return repo_find(parent, required)
