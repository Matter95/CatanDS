import os
from random import randrange

import git

from dice_roll import loose_cards
from gloabl_definitions import HexagonTile, _cost_road, _cost_village, _cost_city, Road_point, Settlement_point, \
    _cost_dev_card, _dev_card_iid, _number_of_players
from utils import (
    update_turn_phase,
    get_all_viable_settlement_points,
    get_all_settlement_points,
    get_all_road_points,
    get_bandit,
    get_player_index,
    get_all_viable_road_points,
    can_build_type,
    get_player_hand,
    get_all_settlements_of_player,
    update_road_point,
    update_player_buildings,
    can_build_something,
    update_player_hand,
    update_bank_resources,
    negate_int_arr,
    update_settlement_point,
    update_active_player,
    get_player_buildings_type,
    update_bank_development_cards,
    get_bank_development_cards,
    can_buy_dev_card,
    get_all_viable_bandit_positions,
    update_bandit,
    get_settlements_adjacent_to_tile,
    update_discard_pile,
    get_sum_of_array
)


def building(repo: git.Repo, hexagons: [HexagonTile]):
    settlement_points = get_all_settlement_points(repo, hexagons)
    road_points = get_all_road_points(repo, hexagons)
    bandit = get_bandit(repo, hexagons)
    local_player = get_player_index(repo.active_branch.name)
    resources = get_player_hand(repo, "resource_cards", local_player)
    viable_sp = get_all_viable_settlement_points(settlement_points, road_points, local_player, bandit)
    viable_rp = get_all_viable_road_points(settlement_points, road_points, local_player, bandit)

    # check if there is a development card that can be used
    playable_cards = get_player_hand(repo, "available_cards", local_player)
    if get_sum_of_array(playable_cards) > 0:
        play_card(repo, playable_cards, local_player, viable_rp, hexagons)
    elif not can_build_something(repo, resources, local_player):
        finish_building(repo, local_player)
    else:
        try_to_build(repo, resources, local_player, settlement_points, viable_rp, viable_sp, [])


def finish_building(repo: git.Repo, local_player: int):
    # next phase
    update = update_turn_phase(repo)
    update = update and update_active_player(repo)


    if update:
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
    else:
        print("update failed in finish building")
        repo.git.reset("--hard", "HEAD")

def build_road(repo: git.Repo, local_player: int, rp: Road_point):
    files = [
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "road_points"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{local_player + 1}"),
    ]

    # update state
    update = update_road_point(repo, rp.index, repo.active_branch.name)
    update = update and update_player_buildings(repo, local_player, [-1, 0, 0])
    update = update and update_player_hand(repo, "resource_cards", local_player, negate_int_arr(list(_cost_road)))
    update = update and update_bank_resources(repo, list(_cost_road))

    if update:
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
    else:
        print("update failed in build road")
        repo.git.reset("--hard", "HEAD")

def build_road_free(repo: git.Repo, local_player: int, rp: Road_point) -> bool:
    # update state
    update = update_road_point(repo, rp.index, repo.active_branch.name)
    update = update and update_player_buildings(repo, local_player, [-1, 0, 0])
    return update

def build_village(repo: git.Repo, local_player: int, sp: Settlement_point):
    files = [
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "settlement_points"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{local_player + 1}"),
    ]

    # update state
    update = update_settlement_point(repo, sp.index, repo.active_branch.name, "Village")
    update = update and update_player_buildings(repo, local_player, [0, -1, 0])
    update = update and update_player_hand(repo, "resource_cards", local_player, negate_int_arr(list(_cost_village)))
    update = update and update_bank_resources(repo, list(_cost_village))

    if update:
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
    else:
        print("update failed in build village")
        repo.git.reset("--hard", "HEAD")

def build_city(repo: git.Repo, local_player: int, village: Settlement_point):
    files = [
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "settlement_points"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{local_player + 1}"),
    ]
    # update state
    update = update_settlement_point(repo, village.index, repo.active_branch.name, "City")
    update = update and update_player_buildings(repo, local_player, [0, 1, -1])
    update = update and update_player_hand(repo, "resource_cards", local_player, negate_int_arr(list(_cost_city)))
    update = update and update_bank_resources(repo, list(_cost_city))

    if update:
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
    else:
        print("update failed in build city")
        repo.git.reset("--hard", "HEAD")

def buy_dev_card(repo: git.Repo, local_player: int):
    files = [
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}",
                                  "resource_cards")
    ]

    dev_cards = get_bank_development_cards(repo)

    index = -1
    viable_card = False
    while not viable_card:
        # draw dev card iid
        index = _dev_card_iid[randrange(len(_dev_card_iid))]
        if dev_cards[index] > 0:
            viable_card = True

    if 0 <= index < len(dev_cards):
        # victory points are unveiled immediately
        if index == 4:
            update_player_hand(repo, "unveiled_cards", local_player, [0,1])
            update_bank_development_cards(repo, [0,0,0,0,-1])
            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "unveiled_cards"))
        else:
            diff = [0,0,0,0,0]
            diff[index] += 1

            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "bought_cards"))
            files.append(os.path.join(repo.working_dir, "state", "game", "bank", "development_cards"))
            update_player_hand(repo, "bought_cards", local_player, diff[0:4])
            update_bank_development_cards(repo, negate_int_arr(diff))

    # update state
    update_player_hand(repo, "resource_cards", local_player, negate_int_arr(list(_cost_dev_card)))
    update_bank_resources(repo, list(_cost_dev_card))

    for file in files:
        repo.index.add(file)

    author_name = repo.active_branch.name
    author = git.Actor(author_name, f"{author_name}@git.com")
    repo.index.commit(
        f"buy_dev_card_player{local_player + 1}",
        [repo.head.commit],
        True,
        author,
        author,
    )

def try_to_build(repo: git.Repo, resources: [int], local_player: int, settlement_points: [Settlement_point], viable_rp: [Road_point], viable_sp: [Settlement_point] ,tried: [str]):
    villages_available = get_player_buildings_type(repo, "Village", local_player)

    # can build a city
    if can_build_type(repo, resources, "City", local_player):
        owned_settlements = get_all_settlements_of_player(settlement_points, local_player)
        villages = []
        for settlement in owned_settlements:
            if settlement.type == "Village":
                villages.append(settlement)
        # pick random village to upgrade
        village = villages[randrange(0, len(villages))]
        build_city(repo, local_player, village)

    # have the resources but cannot build a village
    elif "Village" not in tried and can_build_type(repo, resources, "Village", local_player) and len(viable_sp) == 0:
        if can_build_type(repo, resources, "Road", local_player):
            if len(viable_rp) == 0:
                try_to_build(repo, resources, local_player, settlement_points, viable_rp, viable_sp,
                             ["Village", "Road"])
            else:
                # pick random road point to place road
                rp = viable_rp[randrange(0, len(viable_rp))]
                build_road(repo, local_player, rp)
        else:
            try_to_build(repo, resources, local_player, settlement_points, viable_rp, viable_sp, ["Village", "Road"])
    # can build village
    elif can_build_type(repo, resources, "Village", local_player) and len(viable_sp) > 0:
        # pick random settlement point to place village
        sp = viable_sp[randrange(0, len(viable_sp))]
        build_village(repo, local_player, sp)

    # can build road but should save for a village
    elif can_build_type(repo, resources, "Road", local_player) and len(viable_rp) > 0 and len(viable_sp) >= 1:
        finish_building(repo, local_player)

    # can build road but should save for a city
    elif can_build_type(repo, resources, "Road", local_player) and villages_available <= 2:
        finish_building(repo, local_player)

    # can build road and no villages
    elif can_build_type(repo, resources, "Road", local_player) and len(viable_rp) > 0:
        # pick random road point to place road
        rp = viable_rp[randrange(0, len(viable_rp))]
        build_road(repo, local_player, rp)
    # can buy a development
    elif can_buy_dev_card(repo, resources) and randrange(0, 10) < 1:
        buy_dev_card(repo, local_player)
    else:
        finish_building(repo, local_player)


def play_card(repo: git.Repo, playable_cards, local_player: int, viable_rp: [Road_point], hexagons: [HexagonTile]):
    update = True
    type = -1
    for i, card in enumerate(playable_cards):
        if card > 0:
            type = i
            break
    name = ""
    files = []
    # "Monopoly"
    if type == 0:
        name = "Monopoly"
        for player in range(_number_of_players):
            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player + 1}", "resource_cards"))

        # pick a resource
        resource = randrange(0, 5)

        # all other players loose ALL their cards of that resource
        for player in range(_number_of_players):
            if player != local_player:
                player_has = get_player_hand(repo, "resource_cards", player)
                diff = [0,0,0,0,0]
                diff[resource] += player_has[resource]
                update = update_player_hand(repo, "resource_cards", local_player, diff)
                update = update and update_player_hand(repo, "resource_cards", player, negate_int_arr(diff))

    # "Year-of-Plenty"
    if type == 1:
        name = "Year-of-Plenty"
        files.append(os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"))
        files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}",
                                  "resource_cards"))
        diff = [0,0,0,0,0]
        for _ in range(2):
            resource = randrange(0,5)
            diff[resource] += 1
        update = update and update_player_hand(repo, "resource_cards", local_player, diff)
        update = update and update_bank_resources(repo, negate_int_arr(diff))
    # "Road-Building"
    elif type == 2:
        name = "Road-Building"
        files.append(os.path.join(repo.working_dir, "state", "game", "road_points"))
        files.append(os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{local_player + 1}"))
        rp = viable_rp[randrange(0, len(viable_rp))]
        rp2 = viable_rp[randrange(0, len(viable_rp))]
        while rp == rp2:
            rp2 = viable_rp[randrange(0, len(viable_rp))]

        update = update and build_road_free(repo, local_player, rp)
        update = update and build_road_free(repo, local_player, rp2)

    # "Knight"
    elif type == 3:
        name = "Knight"
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

            diff = [0, 0, 0, 0, 0]

            while stolen == False:
                steal_i = randrange(len(hand))
                if hand[steal_i] > 0:
                    diff[steal_i] += 1
                    break
            update = update and update_player_hand(repo, "resource_cards", local_player, diff)
            update = update and update_player_hand(repo, "resource_cards", steal_from, negate_int_arr(diff))
            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}"))
            files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{steal_from + 1}"))
            files.append(os.path.join(repo.working_dir, "state", "game", "bandit"))

    # move card to discard pile or unveiled cards
    files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}", "available_cards"))
    if type < 3:
        diff = [0,0,0,0]
        diff[type] += 1
        update = update and update_discard_pile(repo, diff[0:3])
        update = update and update_player_hand(repo, "available_cards", local_player, negate_int_arr(diff))
        files.append(os.path.join(repo.working_dir, "state", "game", "discard_pile"))
    else:
        update = update and update_player_hand(repo, "available_cards", local_player, [0,0,0,-1])
        update = update and update_player_hand(repo, "unveiled_cards", local_player, [1,0])
        files.append(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{local_player + 1}",
                                  "unveiled_cards"))

    if update:
        for file in files:
            repo.index.add(file)

        author_name = repo.active_branch.name
        author = git.Actor(author_name, f"{author_name}@git.com")
        repo.index.commit(
            f"play_card_{name}_player{local_player + 1}",
            [repo.head.commit],
            True,
            author,
            author,
        )
    else:
        print("update failed in play card")
        repo.git.reset("--hard", "HEAD")
