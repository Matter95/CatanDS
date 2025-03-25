import os
from math import ceil, floor
from random import randrange

import git

from gloabl_definitions import HexagonTile, _player_colour_2_players, _number_of_players
from repo_utils import get_all_loss_references
from utils import (
    get_active_player,
    get_resources_from_dice_roll,
    get_player_hand,
    get_sum_of_all_resources,
    update_bank_resources,
    update_player_hand,
    negate_int_arr,
    get_player_index,
    update_turn_phase,
    randomly_choose_loss, get_bank_resources, get_diff_between_arrays
)

def roll_dice(repo: git.Repo, hexagons: [HexagonTile]):
    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    active_player = get_active_player(repo)
    local_player = get_player_index(repo.active_branch.name)
    # latest commit
    parent = repo.head.commit
    has_commit = False

    # check if references for loss or empty were created for this player
    for ref in repo.references:
        if ref.name.__contains__(f"loss_player_{local_player + 1}"):
            has_commit = True

    # we already rolled the dice and have a result or are waiting for players to choose their loss
    if (
        parent.message.__contains__("result_")
        or has_commit
    ):
        # check if all players have committed to a loss that need to
        parents = []
        if has_commit:
            if active_player == local_player:
                # check if the current player has committed a loss or empty commit
                children = get_all_loss_references(repo, repo.head.commit)

                # if active player, check if all players committed a loss or empty commit
                if len(children) == _number_of_players:
                    files = []

                    diffs = []

                    current_branch = repo.active_branch.name
                    # merge all commits
                    for child in children:
                        # nothing to merge
                        if child.message.__contains__(f"empty"):
                            pass
                        # hands are mutex, bank needs to be merged
                        else:
                            # get player number of the commit
                            player_nr = child.message
                            index = player_nr.find("player_")
                            player_nr = int(player_nr[index + len("player_"):index + len("player_") + 1])

                            # checkout the branch
                            repo.git.checkout(f"loss_player_{player_nr}")

                            # get the player's hand and the changed bank
                            new_resources = get_player_hand(repo, "resource_cards", player_nr - 1)

                            # add player hand to changed files
                            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_nr}"))

                            # return to active player branch
                            repo.git.checkout(current_branch)

                            old_resources = get_player_hand(repo, "resource_cards", player_nr - 1)

                            diffs.append((player_nr - 1, get_diff_between_arrays(new_resources, old_resources)))

                    bank_diff = [0,0,0,0,0]

                    for player_nr, diff in diffs:
                        update_player_hand(repo, "resource_cards", player_nr, diff)

                        for i in range(len(diff)):
                            bank_diff[i] += abs(diff[i])
                    update_bank_resources(repo, bank_diff)

                    update_turn_phase(repo)
                    files.append(os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"))
                    files.append(os.path.join(repo.working_dir, "state", "game", "turn_phase"))

                    # add files to index
                    for file_path in files:
                        repo.index.add(file_path)
                    repo.index.write_tree()

                    # empty commit
                    repo.index.commit(
                        f"roll_dice_merge",
                        children,
                        True,
                        author,
                        author,
                    )

                    # delete references
                    for i in range(_number_of_players):
                        repo.delete_head(f"loss_player_{i + 1}", force=True)

        else:
            index = parent.message.find("result_")
            roll = int(parent.message[index + len("result_"):])
            if roll == 7:
                # no resource gain this round, check if player has more than 7 cards
                resources = get_player_hand(repo, "resource_cards", local_player)
                cards = get_sum_of_all_resources(resources)

                # loose half the cards (ceil(cards/2))
                if cards > 7:
                    loose_cards(repo, cards, resources, local_player, repo.head.commit)

                # everything stays the same
                else:
                    current_branch = repo.active_branch.name
                    # checkout the branch
                    repo.git.checkout("-b", f"loss_player_{local_player + 1}")

                    # empty commit
                    commit = repo.index.commit(
                        f"roll_dice_player_{local_player + 1}_empty",
                        [parent],
                        True,
                        author,
                        author,
                    )

                    repo.git.checkout(current_branch)
            else:
                if active_player == local_player:
                    files = []
                    for player in _player_colour_2_players:
                        player_index = get_player_index(player)
                        gain = get_resources_from_dice_roll(repo, hexagons, roll, player_index)
                        update_player_hand(repo, "resource_cards", player_index, gain)
                        update_bank_resources(repo, negate_int_arr(gain))

                        if gain != [0,0,0,0,0]:
                            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_index + 1}",
                                         "resource_cards"))

                    files.append(os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"))
                    files.append(os.path.join(repo.working_dir, "state", "game", "turn_phase"))
                    update_turn_phase(repo)

                    # add files to index
                    for file_path in files:
                        repo.index.add(file_path)
                    repo.index.write_tree()

                    author = git.Actor(author_name, f"{author_name}@git.com")
                    repo.index.commit(
                        f"roll_dice_player_{local_player + 1}_gain",
                        [parent],
                        True,
                        author,
                        author,
                    )
    else:
        local_player = get_player_index(repo.active_branch.name)

        if active_player == local_player:
            result = randrange(2, 12)

            # send dice result to all other players
            repo.index.commit(
                f"roll_dice_player_{local_player + 1}_result_{result}",
                [parent],
                True,
                author,
                author,
            )

def loose_cards(repo: git.Repo, cards: int, resources: [int], local_player: int, parent):
    loss = floor(cards / 2)
    diff = randomly_choose_loss(loss, resources)

    current_branch = repo.active_branch.name
    # checkout the branch
    repo.git.checkout("-b", f"loss_player_{local_player + 1}")

    update_player_hand(repo, "resource_cards", local_player, diff)
    update_bank_resources(repo, negate_int_arr(diff))

    files = [
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}",
                     "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
    ]

    # add files to index
    for file_path in files:
        repo.index.add(file_path)
    repo.index.write_tree()

    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    commit = repo.index.commit(
        f"roll_dice_player_{local_player + 1}_loss",
        [parent],
        True,
        author,
        author,
    )
    # switch back
    repo.git.checkout(current_branch)
