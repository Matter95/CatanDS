import os
from random import randrange

import git

from gloabl_definitions import HexagonTile, _cost_road, _cost_village, _cost_city, Road_point, Settlement_point, \
    _cost_dev_card
from utils import (
    update_turn_phase,
    get_all_viable_settlement_points,
    get_all_settlement_points,
    get_all_road_points,
    get_bandit,
    get_player_index,
    get_all_viable_road_points,
    can_build_type,
    get_player_hand, get_all_settlements_of_player, update_road_point, update_player_buildings, can_build_something,
    update_player_hand, update_bank_resources, negate_int_arr, update_settlement_point, update_active_player,
    get_player_buildings_type, update_bank_development_cards, get_bank_development_cards, can_buy_dev_card
)


def building(repo: git.Repo, hexagons: [HexagonTile]):
    settlement_points = get_all_settlement_points(repo, hexagons)
    road_points = get_all_road_points(repo, hexagons)
    bandit = get_bandit(repo, hexagons)
    local_player = get_player_index(repo.active_branch.name)
    resources = get_player_hand(repo, "resource_cards", local_player)
    villages = get_player_buildings_type(repo, "Village", local_player)
    viable_sp = get_all_viable_settlement_points(settlement_points, road_points, local_player, bandit)
    viable_rp = get_all_viable_road_points(settlement_points, road_points, local_player, bandit)

    if not can_build_something(repo, resources, local_player):
        finish_building(repo, local_player)
    else:
        files = []
        # can build a city
        if can_build_type(repo, resources, "City", local_player):
            villages = get_all_settlements_of_player(settlement_points, local_player)

            # pick random village to upgrade
            village = villages[randrange(0, len(villages))]
            build_city(repo, local_player, village)

        # have the arr but cannot build a village
        elif can_build_type(repo, resources, "Village", local_player) and len(viable_sp) == 0:
            if can_build_type(repo, resources, "Road", local_player):
                # pick random road point to place road
                rp = viable_rp[randrange(0, len(viable_rp))]
                build_road(repo, local_player, rp)
            else:
                finish_building(repo, local_player)
        # can build village
        elif can_build_type(repo, resources, "Village", local_player) and len(viable_sp) > 0:
            # pick random settlement point to place village
            sp = viable_sp[randrange(0, len(viable_sp))]
            build_village(repo, local_player, sp)

        # can build road but should save for a village
        elif can_build_type(repo, resources, "Road", local_player) and len(viable_rp) > 0 and len(viable_sp) >= 1:
            finish_building(repo, local_player)

        # can build road but should save for a city
        elif can_build_type(repo, resources, "Road", local_player) and villages >= 3:
            finish_building(repo, local_player)

        # can build road and no villages
        elif can_build_type(repo, resources, "Road", local_player) and len(viable_rp) > 0:
            # pick random road point to place road
            rp = viable_rp[randrange(0, len(viable_rp))]
            build_road(repo, local_player, rp)
        # can buy a development
        elif can_buy_dev_card(repo, resources):
            buy_dev_card(repo, local_player)
        else:
            finish_building(repo, local_player)

def finish_building(repo: git.Repo, local_player: int):
    # next phase
    update_turn_phase(repo)
    update_active_player(repo)

    # add files to index
    repo.index.add(os.path.join(repo.working_dir, "state", "game", "turn_phase"))
    repo.index.add(os.path.join(repo.working_dir, "state", "game", "active_player"))

    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    repo.index.commit(
        f"finish_building_player_{local_player + 1}",
        [repo.head.commit],
        True,
        author,
        author,
    )


def build_road(repo: git.Repo, local_player: int, rp: Road_point):
    files = [
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "road_points"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{local_player + 1}"),
    ]

    # update state
    update_road_point(repo, rp.index, repo.active_branch.name)
    update_player_buildings(repo, local_player, [-1, 0, 0])
    update_player_hand(repo, "resource_cards", local_player, negate_int_arr(list(_cost_road)))
    update_bank_resources(repo, list(_cost_road))

    for file in files:
        repo.index.add(file)

    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    repo.index.commit(
        f"build_road_player{local_player + 1}",
        [repo.head.commit],
        True,
        author,
        author,
    )

def build_village(repo: git.Repo, local_player: int, sp: Settlement_point):
    files = [
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "settlement_points"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{local_player + 1}"),
    ]

    # update state
    update_settlement_point(repo, sp.index, repo.active_branch.name, "Village")
    update_player_buildings(repo, local_player, [0, -1, 0])
    update_player_hand(repo, "resource_cards", local_player, negate_int_arr(list(_cost_village)))
    update_bank_resources(repo, list(_cost_village))

    for file in files:
        repo.index.add(file)

    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    repo.index.commit(
        f"build_village_player{local_player + 1}",
        [repo.head.commit],
        True,
        author,
        author,
    )

def build_city(repo: git.Repo, local_player: int, village: Settlement_point):
    files = [
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "settlement_points"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{local_player + 1}"),
    ]

    # update state
    update_settlement_point(repo, village.index, repo.active_branch.name, "City")
    update_player_buildings(repo, local_player, [0, 1, -1])
    update_player_hand(repo, "resource_cards", local_player, negate_int_arr(list(_cost_city)))
    update_bank_resources(repo, list(_cost_city))

    for file in files:
        repo.index.add(file)

    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    repo.index.commit(
        f"build_city_player{local_player + 1}",
        [repo.head.commit],
        True,
        author,
        author,
    )


def buy_dev_card(repo: git.Repo, local_player: int):
    files = [
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "bank", "development_cards"),
        os.path.join(repo.working_dir, "state", "game", "settlement_points"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "bought_cards"),
    ]

    dev_cards = get_bank_development_cards(repo)

    index = -1
    viable_card = False
    while viable_card:
        index = randrange(len(dev_cards))
        if dev_cards[index] > 0:
            viable_card = True

    if 0 <= index < len(dev_cards):
        # victory points are revealed immediately
        if index > 4:

        else:
            diff = [0,0,0]
            diff[index] += 1

    # update state
    update_player_hand(repo, "resource_cards", local_player, negate_int_arr(list(_cost_dev_card)))
    update_bank_resources(repo, list(_cost_city))

    update_player_hand(repo, "bought_cards", local_player, diff)
    update_bank_development_cards(repo, negate_int_arr(diff))

    for file in files:
        repo.index.add(file)

    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    repo.index.commit(
        f"build_city_player{local_player + 1}",
        [repo.head.commit],
        True,
        author,
        author,
    )