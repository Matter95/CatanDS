import os
from math import ceil
from random import randrange

import git

from gloabl_definitions import HexagonTile
from repo_utils import get_repo_author_gitdir
from utils import get_active_player, get_resources_from_dice_roll, get_player_hand, get_sum_of_all_resources, \
    update_bank_resources, update_player_hand, negate_int_arr


def roll_dice(repo: git.Repo, hexagons: [HexagonTile], parent: git.Commit) -> git.Commit:
    author_name = get_repo_author_gitdir(repo.git_dir)
    author = git.Actor(author_name, f"{author_name}@git.com")
    active_player = get_active_player(repo)

    # we already rolled the dice and have a result
    if parent.message.__contains__("result_"):
        index = parent.message.find("result_")
        roll = int(parent.message[index + len("result_"):])

        if roll == 7:
            # no resource gain this round, check if player has more than 7 cards
            resources = get_player_hand(repo, "resource_cards", active_player)
            cards = get_sum_of_all_resources(resources)

            # loose half the cards (ceil(cards/2))
            if cards > 7:
                loss = ceil(cards / 2)

                diff = [0,0,0,0,0]

                # choose cards to loose
                for i in range(0, loss):
                    index = randrange(0, 5)
                    if resources[index] - diff[index] - 1 > 0:
                        diff[index] -= 1

                update_player_hand(repo, "resource_cards", active_player, diff)
                update_bank_resources(repo, negate_int_arr(diff))

                files = [
                    os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{active_player + 1}",
                                 "resource_cards"),
                    os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
                ]

                # add files to index
                for file_path in files:
                    repo.index.add(file_path)
                repo.index.write_tree()

                author = git.Actor(author_name, f"{author_name}@git.com")
                commit_id = repo.index.commit(
                    f"roll_dice_player_{active_player}_loss",
                    [parent],
                    True,
                    author,
                    author,
                )

                return commit_id

            # everything stays the same
            else:
                # empty commit
                commit_id = repo.index.commit(
                    f"roll_dice_player_{active_player}_empty",
                    [parent],
                    True,
                    author,
                    author,
                )
                return commit_id
        else:
            gain = get_resources_from_dice_roll(repo, hexagons, roll, active_player)

            files = [
                os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{active_player + 1}",
                             "resource_cards"),
                os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
            ]

            # add files to index
            for file_path in files:
                repo.index.add(file_path)
            repo.index.write_tree()

            author = git.Actor(author_name, f"{author_name}@git.com")
            commit_id = repo.index.commit(
                f"roll_dice_player_{active_player}_gain",
                [parent],
                True,
                author,
                author,
            )
    # we need merge all gains, loss choices or empty commits
    elif parent.message.__contains__("_gain") or parent.message.__contains__("_empty") or parent.message.__contains__("_loss"):
        parents = []
        if parent.message.__contains__("_gain"):
            for ref in repo.references:
                if ref.commit.message.__contains__("_gain"):
                    parents.append(ref.commit)
        else:
            for ref in repo.references:
                if ref.commit.message.__contains__("_loss") or ref.commit.message.__contains__("_empty"):
                    parents.append(ref.commit)

    else:
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