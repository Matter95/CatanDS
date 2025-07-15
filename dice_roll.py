import os
from functools import partial
from math import floor
from random import randrange

import git

from gloabl_definitions import HexagonTile, _number_of_players, get_player_colour
from repo_utils import get_all_loss_references
from utils import (
    get_active_player,
    get_resources_from_dice_roll,
    get_player_hand,
    get_sum_of_array,
    update_bank_resources,
    update_player_hand,
    negate_int_arr,
    get_player_index,
    update_turn_phase,
    randomly_choose_loss,
    get_diff_between_arrays,
    get_all_viable_bandit_positions,
    update_bandit,
    get_settlements_adjacent_to_tile
)

def roll_dice(repo: git.Repo, hexagons: [HexagonTile]):
    """
    Starts the roll dice phase. Players earn resources, loose resources or/and move the bandit. Reconciles the
    concurrency happening when players need to choose which resource cards to lose.

    Parameters
    ----------
    repo: current repo
    hexagons: map tiles
    """
    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    active_player = get_active_player(repo)
    local_player = get_player_index(repo.active_branch.name)
    # latest commit
    parent = repo.head.commit
    has_commit = False

    # check if references for loss or empty were created for this player
    for ref in repo.references:
        if ref.name.__contains__(f"{parent}_loss_{author_name}"):
            has_commit = True
            break

    update = True
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
                            player_colour = child.message
                            index = player_colour.find("loss_")
                            player_colour = player_colour[index + len("loss_"):]
                            player_nr = get_player_index(player_colour)

                            # checkout the branch
                            repo.git.checkout(f"{parent}_loss_{player_colour}")
                            # get the player's hand
                            new_resources = get_player_hand(repo, "resource_cards", player_nr)

                            # add player hand to changed files
                            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_nr + 1}"))

                            # return to active player branch
                            repo.git.checkout(current_branch)

                            old_resources = get_player_hand(repo, "resource_cards", player_nr)

                            diffs.append((player_nr, get_diff_between_arrays(new_resources, old_resources)))

                    bank_diff = [0,0,0,0,0]

                    for player_nr, diff in diffs:
                        update = update and update_player_hand(repo, "resource_cards", player_nr, diff)

                        for i in range(len(diff)):
                            bank_diff[i] += abs(diff[i])
                    update = update and update_bank_resources(repo, bank_diff)

                    # move bandit
                    bandit_positions = get_all_viable_bandit_positions(repo, hexagons, local_player)

                    choice = bandit_positions[randrange(len(bandit_positions))]
                    update = update and update_bandit(repo, hexagons, choice.id)

                    # steal a random resource
                    sp_steal = get_settlements_adjacent_to_tile(repo, hexagons, choice)
                    if sp_steal:
                        sp = sp_steal[randrange(len(sp_steal))]
                        stolen = False
                        steal_from = get_player_index(sp.owner)
                        hand = get_player_hand(repo, "resource_cards", steal_from)

                        diff = [0,0,0,0,0]

                        while stolen == False:
                            if hand == [0,0,0,0,0]:
                                break
                            steal_i = randrange(len(hand))
                            if hand[steal_i] > 0:
                                diff[steal_i] += 1
                                break

                        update = update and update_player_hand(repo, "resource_cards", local_player, diff)
                        update = update and update_player_hand(repo, "resource_cards", steal_from, negate_int_arr(diff))
                        files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}"))
                        files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{steal_from + 1}"))

                    update = update and update_turn_phase(repo)
                    files.append(os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"))
                    files.append(os.path.join(repo.working_dir, "state", "game", "turn_phase"))
                    files.append(os.path.join(repo.working_dir, "state", "game", "bandit"))

                    if update:
                        # add files to index
                        for file_path in files:
                            repo.index.add(file_path)
                        repo.index.write_tree()

                        # empty commit
                        repo.index.commit(
                            f"roll_dice_steal_and_merge",
                            children,
                            True,
                            author,
                            author,
                        )

                    else:
                        print("update failed in dice roll merge")
                        repo.git.reset("--hard", "HEAD")

        else:
            index = parent.message.find("result_")
            roll = int(parent.message[index + len("result_"):])
            if roll == 7:
                # no resource gain this round, check if player has more than 7 cards
                resources = get_player_hand(repo, "resource_cards", local_player)
                cards = get_sum_of_array(resources)

                # loose half the cards (ceil(cards/2))
                if cards > 7:
                    loose_cards(repo, cards, resources, local_player, repo.head.commit)

                # everything stays the same
                else:
                    current_branch = repo.active_branch.name
                    # checkout the branch
                    repo.git.checkout("-b", f"{parent}_loss_{current_branch}")

                    # empty commit
                    repo.index.commit(
                        f"loss_{current_branch}_empty",
                        [parent],
                        True,
                        author,
                        author,
                    )
                    repo.git.checkout(current_branch)
            else:
                if active_player == local_player:
                    files = []
                    for player in get_player_colour(_number_of_players):
                        gain = [0,0,0,0,0]
                        player_index = get_player_index(player)
                        gain = get_resources_from_dice_roll(repo, hexagons, roll, player_index)
                        update = update and update_player_hand(repo, "resource_cards", player_index, gain)
                        update = update and update_bank_resources(repo, negate_int_arr(gain))

                        if gain != [0,0,0,0,0]:
                            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_index + 1}",
                                                      "resource_cards"))

                    files.append(os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"))
                    files.append(os.path.join(repo.working_dir, "state", "game", "turn_phase"))
                    update = update and update_turn_phase(repo)


                    if update:
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
                        print("update failed in dice roll gain")
                        repo.git.reset("--hard", "HEAD")
    else:
        local_player = get_player_index(repo.active_branch.name)

        if active_player == local_player:
            # if there are bought cards, move them to available cards
            cards = get_player_hand(repo, "bought_cards", local_player)
            card_sum = get_sum_of_array(cards)

            if card_sum > 0:
                update = update_player_hand(repo, "available_cards", local_player, cards)
                update = update and update_player_hand(repo, "bought_cards", local_player, negate_int_arr(cards))

                repo.index.add(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "bought_cards"))
                repo.index.add(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "available_cards"))

            die1 = randrange(1, 7)
            die2 = randrange(1, 7)
            result = die1 + die2

            if update:
                # send dice result to all other players
                repo.index.commit(
                    f"roll_dice_player_{local_player + 1}_result_{result}",
                    [parent],
                    True,
                    author,
                    author,
                )
            else:
                print("update failed in dice roll result")
                repo.git.reset("--hard", "HEAD")

def loose_cards(repo: git.Repo, cards: int, resources: [int], local_player: int, parent: git.Commit):
    """
    Players choose which cards they lose given a 7 as dice result while a player owns more than 7 cards.

    Parameters
    ----------
    repo: current repo
    cards: a players resource cards summed up
    resources: a players resource cards
    local_player: player number
    parent: parent commit
    """
    loss = floor(cards / 2)
    diff = randomly_choose_loss(loss, resources)
    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")

    current_branch = repo.active_branch.name
    # checkout the branch
    repo.git.checkout("-b", f"{parent}_loss_{current_branch}")

    update = update_player_hand(repo, "resource_cards", local_player, diff)
    update = update and update_bank_resources(repo, negate_int_arr(diff))

    files = [
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}",
                     "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
    ]

    if update:
        # add files to index
        for file_path in files:
            repo.index.add(file_path)
        repo.index.write_tree()


        repo.index.commit(
            f"loss_{current_branch}",
            [parent],
            True,
            author,
            author,
        )
    else:
        print("failed update in loose cards")
    # switch back
    repo.git.checkout(current_branch)
