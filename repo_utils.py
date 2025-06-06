import os.path

import git
from git import Repo


def init_repo(path: str, repo_name: str, author: str, email: str, bare: bool) -> git.Repo:
    """
    initialize a git repository with the given path and name
    :param path: directory to create the repository in
    :param repo_name: repository name
    :param author: author's name
    :param email: author's email
    :param bare: create bare or non-bare repository
    :return: git.Repo object
    """
    if bare:
        # do not create master branch
        repo = Repo.init(f"{path}/{repo_name}", initial_branch=f"{repo_name}", bare=True)
    else:
        # do not create master branch
        repo = Repo.init(f"{path}/{repo_name}", initial_branch=f"{repo_name}")

    author = git.Actor(author, email)
    empty_tree = repo.index.write_tree()

    initial_commit = repo.index.commit(
        "initial commit",
        [],
        True,
        author,
        author,
    )
    print(f"Repository {repo_name} created\n with latest commit: {initial_commit}\n and tree id: {empty_tree}")

    return repo


def get_all_loss_references(repo: git.Repo, commit: git.Commit):
    children = []
    for ref in repo.references:
        if ref.name.__contains__("loss_") and commit in ref.commit.parents:
            children.append(ref.commit)
    return children
