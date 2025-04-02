import os
import shutil

import git

from repo_utils import init_repo


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def delete_repo(repo_path: str, repo_name: str) -> None:
    """
    deletes the given repository

    Parameters
    ----------
    repo_path : repository path
    repo_name : repository name
    """
    if os.path.exists(os.path.join(repo_path, repo_name)):
        # remove directory
        shutil.rmtree(os.path.join(repo_path, repo_name), onerror=onerror)


def create_repo(repo_path: str, repo_name: str, author: str, email: str) -> git.Repo:
    """
    Creates a repo with the given parameters.

    Parameters
    ----------
    repo_path : repository path
    repo_name : repository name
    author : author name
    email : author email

    Returns
    -------
    repo
    """
    return init_repo(repo_path, repo_name, author, email, False)