import os
from random import randrange

import git

from gloabl_definitions import HexagonTile, Wharfs
from utils import (
    update_turn_phase,
    get_player_index,
    get_player_hand,
    get_all_settlement_points,
    get_all_settlements_of_player,
    update_player_hand,
    update_bank_resources,
    negate_int_arr,
    can_build_something, get_player_buildings_type
)



def trading(repo: git.Repo, hexagons: [HexagonTile]):
    local_player = get_player_index(repo.active_branch.name)
    resources = get_player_hand(repo, "resource_cards", local_player)
    # already used up all villages, should build cities
    villages = get_player_buildings_type(repo, "Village", local_player)

    # if the player cannot build anything, trade randomly
    if can_build_something(repo, resources, local_player) and villages != 5:

        # no need to trade
        finish_trading(repo, local_player)
    else:
        settlements = get_all_settlements_of_player(get_all_settlement_points(repo, hexagons), local_player)
        # check ports available to player

        available_ports = [[],[],[],[],[]]

        for wharf in Wharfs:
            for settlement in settlements:
                if hexagons[wharf.coords[0]] in settlement.coords and hexagons[wharf.coords[1]] in settlement.coords:
                    if wharf.type == "3:1":
                        for i in range(len(available_ports)):
                            if wharf.type not in available_ports[i]:
                                available_ports[i].append(wharf.type)
                    elif wharf.type == "Lumber":
                        if wharf.type not in available_ports[0]:
                            available_ports[0].append("2:1")
                    elif wharf.type == "Brick":
                        if wharf.type not in available_ports[1]:
                            available_ports[1].append("2:1")
                    elif wharf.type == "Wool":
                        if wharf.type not in available_ports[2]:
                            available_ports[2].append("2:1")
                    elif wharf.type == "Grain":
                        if wharf.type not in available_ports[3]:
                            available_ports[3].append("2:1")
                    elif wharf.type == "Lumber":
                        if wharf.type not in available_ports[4]:
                            available_ports[4].append("2:1")

        no_trade = True

        can_trade = False
        resource_can_trade = []
        for i, resource in enumerate(resources):
            trade_cost = 4
            if "2:1" in available_ports[i]:
                trade_cost = 2
            elif "3:1" in available_ports[i]:
                trade_cost = 3
            if resource >= trade_cost:
                resource_can_trade.append(i)
                can_trade = True

        if not can_trade:
            finish_trading(repo, local_player)
        else:
            resource_zero = []

            for i, resource in enumerate(resources):
                if resource == 0:
                    resource_zero.append(i)
            while no_trade:
                # pick a random resource to trade with
                trade_resource = resource_can_trade[randrange(len(resource_can_trade))]

                trade_cost = 4
                if "2:1" in available_ports[trade_resource]:
                    trade_cost = 2
                elif "3:1" in available_ports[trade_resource]:
                    trade_cost = 3

                if resources[trade_resource] >= trade_cost:
                    buy_resource = trade_resource
                    # pick a random resource, but not the one we are paying with
                    while buy_resource == trade_resource:
                        if not resource_zero:
                            buy_resource = randrange(3, 5)
                        else:
                            buy_resource = resource_zero[randrange(len(resource_zero))]
                else:
                    continue

                hand_diff = [0,0,0,0,0]
                hand_diff[trade_resource] -= trade_cost
                hand_diff[buy_resource] += 1

                # update bank and player hand
                update_player_hand(repo, "resource_cards", local_player, hand_diff)
                update_bank_resources(repo, negate_int_arr(hand_diff))

                files = [
                    os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
                    os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}")
                ]

                for file in files:
                    repo.index.add(file)

                author_name = repo.active_branch.name
                author = git.Actor(author_name, f"{author_name}@git.com")
                repo.index.commit(
                    f"trade_player{local_player + 1}",
                    [repo.head.commit],
                    True,
                    author,
                    author,
                )
                no_trade = False

def finish_trading(repo: git.Repo, local_player: int):
    # next phase
    update_turn_phase(repo)

    # add files to index
    repo.index.add(os.path.join(repo.working_dir, "state", "game", "turn_phase"))
    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    repo.index.commit(
        f"finish_trading_player{local_player + 1}",
        [repo.head.commit],
        True,
        author,
        author,
    )