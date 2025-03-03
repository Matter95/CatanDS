import git


def initialize_game_state(
        repo: git.Repo,
) -> git.Commit:
    """
    Initializes the game and initialization state.

    Parameters
    ----------
    repo : working repository

    Returns
    -------
    initial git Commit
    """