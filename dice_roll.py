from random import randrange

import git

from repo_utils import get_repo_author_gitdir
from utils import get_active_player


def roll_dice(repo: git.Repo, parent: git.Commit) -> git.Commit:
    author_name = get_repo_author_gitdir(repo.git_dir)
    author = git.Actor(author_name, f"{author_name}@git.com")
    active_player = get_active_player(repo)

    result = randrange(2,12)

    # send dice result to all other players
    commit_id = repo.index.commit(
        f"roll_dice_player_{active_player}_result_{result}",
        [parent],
        True,
        author,
        author,
    )

    # does not change head
    return commit_id