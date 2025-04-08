import os
from random import randrange
from typing import List

import git

from gloabl_definitions import (
    Settlement_point,
    HexagonTile,
    Road_point,
    ROOT_DIR,
    _resource_card_pool,
    _number_of_players,
    _development_card_pool,
    _player_building_pool,
    TEST_DIR, _player_colour_reversed_2_players, _cost_village, _cost_city, _cost_road, _cost_dev_card,
    get_player_colour,
)
from repo_utils import init_repo


def create_folder_structure(repo: git.Repo, n_players: int):
    """
    Creates the base folder structure that keeps the game state

    Parameters
    ----------
    repo : current repo
    n_players : number of players
    """
    folders = [
        os.path.join(repo.working_dir, "state"),
        os.path.join(repo.working_dir, "state", "game"),
        os.path.join(repo.working_dir, "state", "game", "bank"),
        os.path.join(repo.working_dir, "state", "game", "player_hands"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings"),
        os.path.join(repo.working_dir, "state", "initialization"),
    ]

    for i in range(n_players):
        folders += [
            os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{i + 1}"),
        ]

    for path in folders:
        if not os.path.exists(path):
            os.makedirs(path)


def init_phase_next(current_phase: str) -> str:
    """
    Returns the next init phase

    Parameters
    ----------
    current_phase : current initialization phase

    Returns
    ----------
    next initialization phase
    """
    if current_phase == "phase_one":
        return "phase_two"
    elif current_phase == "phase_two":
        return "phase_two"
    else:
        return ""


def turn_phase_next(current_phase: str) -> str:
    """
    Returns the next turn phase

    Parameters
    ----------
    current_phase : current turn phase

    Returns
    ----------
    next turn phase
    """
    if current_phase == "bot":
        return "dice_roll"
    elif current_phase == "dice_roll":
        return "trading"
    elif current_phase == "trading":
        return "building"
    elif current_phase == "building":
        return "dice_roll"
    else:
        print(f"illegal turn phase: {current_phase}")
        return ""


# getter and setter for the files
def get_initial_phase(repo: git.Repo):
    """
    Reads initial phase from the file

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    init phase or None
    """
    try:
        with open(os.path.join(repo.working_dir, "state", "initialization", "init_phase"), "r") as file:
            line = file.readline()
        return line
    except FileNotFoundError:
        return None


def update_initial_phase(repo: git.Repo):
    """
    Updates initial phase and modifies the file

    Parameters
    ----------
    repo : current repo
    """
    # load old value
    old_val = get_initial_phase(repo)
    # get next phase
    new_val = init_phase_next(old_val)

    with open(os.path.join(repo.working_dir, "state", "initialization", "init_phase"), "w") as file:
        file.write(f"{new_val}")
    return True


def get_initial_active_player(repo: git.Repo):
    """
    Gets the active player from the file (initial phase)

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    init phase or None
    """
    with open(os.path.join(repo.working_dir, "state", "initialization", "active_player"), "r") as file:
        line = file.readline()
    return int(line)


def get_player_index(colour: str) -> int | None:
    """
    Returns the player number given the player's colour.

    Parameters
    ----------
    colour : player colour

    Returns
    -------
    player number
    """
    index = colour.find("_")
    if index != -1:
        colour = colour[:index]
    for i, c in enumerate(get_player_colour(_number_of_players)):
        if c == colour:
            return i


def update_initial_active_player(repo: git.Repo) -> bool:
    """
    Updates the active player and modifies the file (initial phase)

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    success
    """
    old_val = int(get_initial_active_player(repo))

    new_val = (old_val + 1) % _number_of_players

    with open(os.path.join(repo.working_dir, "state", "initialization", "active_player"), "w") as file:
        file.write(f"{new_val}")
    return True


def update_initial_active_player_rev(repo: git.Repo) -> bool:
    """
    Updates the active player and modifies the file (initial phase). The player order is reversed.


    Parameters
    ----------
    repo : current repo


    Returns
    -------
    success
    """
    old_val = int(get_initial_active_player(repo))

    new_val = (old_val - 1) % _number_of_players

    with open(os.path.join(repo.working_dir, "state", "initialization", "active_player"), "w") as file:
        file.write(f"{new_val}")
    return True


def get_active_player(repo: git.Repo) -> str:
    """
    Gets the active player from the file

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    active player
    """
    with open(os.path.join(repo.working_dir, "state", "game", "active_player"), "r") as file:
        line = file.readline()
    return int(line)


def update_active_player(repo: git.Repo) -> bool:
    """
    Updates the active player and modifies the file

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    success
    """
    old_val = get_active_player(repo)

    new_val = (old_val + 1) % _number_of_players

    with open(os.path.join(repo.working_dir, "state", "game", "active_player"), "w") as file:
        file.write(f"{new_val}")
    return True


def get_turn_phase(repo: git.Repo) -> str:
    """
    Gets the turn phase from the file

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    turn phase
    """
    with open(os.path.join(repo.working_dir, "state", "game", "turn_phase"), "r") as file:
        line = file.readline()
    return line


def update_turn_phase(repo: git.Repo, win: bool = False) -> bool:
    """
    Updates initial phase and modifies the file

    Parameters
    ----------
    repo : current repo
    win: someone won the game

    Returns
    -------
    success
    """
    # load old value
    old_val = get_turn_phase(repo)
    # get next phase
    new_val = turn_phase_next(old_val)

    if win:
        new_val = "top"

    with open(os.path.join(repo.working_dir, "state", "game", "turn_phase"), "w") as file:
        file.write(f"{new_val}")
    return True


# player functions
def get_player_hand(repo: git.Repo, hand_type: str, player_nr: int) -> List[int] | None:
    """
    Gets a players hand given a hand type from file.

    Parameters
    ----------
    repo: current repo
    hand_type: type of card we want to get
    player_nr: current player number

    Returns
    -------
    cards of hand type or None
    """
    if hand_type == "resource_cards":
        vals = [0, 0, 0, 0, 0]
    elif hand_type == "bought_cards":
        vals = [0, 0, 0, 0]
    elif hand_type == "available_cards":
        vals = [0, 0, 0, 0]
    elif hand_type == "unveiled_cards":
        vals = [0, 0]
    else:
        return None

    with open(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_nr + 1}", hand_type),
              "r") as file:
        line = file.readline()
        line = line.split(",")

        for i, val in enumerate(line):
            vals[i] = int(val)

    return vals


def update_player_hand(repo: git.Repo, hand_type: str, player_nr: int, update_diff: [int]) -> bool:
    """
    Updates initial phase and modifies the file

    Parameters
    ----------
    repo: current repo
    hand_type: type of card we want to get
    player_nr: current player number
    update_diff: card difference to be added (or subtracted)

    Returns
    -------
    success
    """
    path = os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_nr + 1}")

    old_val = get_player_hand(repo, hand_type, player_nr)

    if hand_type == "resource_cards":
        empty = [0, 0, 0, 0, 0]
        path = os.path.join(path, "resource_cards")
    elif hand_type == "bought_cards":
        empty = [0, 0, 0, 0]
        path = os.path.join(path, "bought_cards")
    elif hand_type == "available_cards":
        empty = [0, 0, 0, 0]
        path = os.path.join(path, "available_cards")
    elif hand_type == "unveiled_cards":
        empty = [0, 0]
        path = os.path.join(path, "unveiled_cards")
    else:
        print(f"illegal hand_type: {hand_type}")
        return False

    if len(update_diff) == len(empty):
        if update_diff != empty:
            new_val = []
            for i, val in enumerate(update_diff):
                if hand_type == "resource_cards":
                    if 0 > old_val[i] + val or old_val[i] + val > _resource_card_pool[i]:
                        print(
                            f"illegal update: Available {old_val[i]}, add {update_diff[i]}, max {_resource_card_pool[i]}")
                        return False
                else:
                    j = i
                    if hand_type == "unveiled_cards":
                        j += 3
                    if 0 > old_val[i] + val or old_val[i] + val > _development_card_pool[j]:
                        print(
                            f"illegal update: Available {old_val[i]}, add {update_diff[i]}, max {_resource_card_pool[i]}")
                        return False
                new_val.append(old_val[i] + val)
            with open(path, "w") as file:
                file.write(f"{new_val}".replace("[", "").replace("]", "").replace(" ", ""))
    else:
        print("length of diff not equal to hand to be updated")
        return False
    return True


def get_player_buildings(repo: git.Repo, player_nr: int) -> [int]:
    """
    Reads a players remaining buildings from file

    Parameters
    ----------
    repo : current repo
    player_nr: current player number

    Returns
    -------
    player buildings
    """
    path = os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{player_nr + 1}")
    buildings: [int] = []
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for element in line:
            buildings.append(int(element))
    return buildings


def get_player_buildings_type(repo: git.Repo, building_type: str, player_nr: int) -> int | None:
    """
    Reads a players remaining buildings from file and filters it by a specific building type.

    Parameters
    ----------
    repo : current repo
    building_type: type of building to filter by
    player_nr: current player number

    Returns
    -------
    init phase or None
    """
    buildings = get_player_buildings(repo, player_nr)
    if building_type == "Road":
        building = buildings[0]
    elif building_type == "Village":
        building = buildings[1]
    elif building_type == "City":
        building = buildings[2]
    else:
        print("illegal building type")
        return None

    return building


def update_player_buildings(repo: git.Repo, player_nr: int, update_diff: [int]) -> bool:
    """
    Updates a player's remaining buildings and modifies the file

    Parameters
    ----------
    repo : current repo
    player_nr: current player number
    update_diff: card difference to be added (or subtracted)

    Returns
    -------
    success
    """
    path = os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{player_nr + 1}")

    old_val = get_player_buildings(repo, player_nr)

    if update_diff != [0, 0, 0]:
        new_val = []
        for i, val in enumerate(update_diff):
            if 0 > old_val[i] + val or old_val[i] + val > _player_building_pool[i]:
                print(f"PLAYER BUILDING: illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
                return False
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            file.write(f"{new_val}".replace("[", "").replace("]", "").replace(" ", ""))
    return True


# bank functions
def get_bank_resources(repo: git.Repo):
    """
    Reads the banks resource cards from the file

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    banks resource cards
    """
    path = os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards")
    resource_cards = [0, 0, 0, 0, 0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            resource_cards[i] = int(val)

    return resource_cards


def update_bank_resources(repo: git.Repo, update_diff: [int]) -> bool:
    """
    Updates the banks resource cards and modifies the file


    Parameters
    ----------
    repo : current repo
    update_diff: card difference to be added (or subtracted)

    Returns
    -------
    success
    """
    if len(update_diff) != 5:
        print(f"illegal update length: {len(update_diff)} not 5")
        return False

    path = os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards")
    # load old value
    old_val = get_bank_resources(repo)

    if update_diff != [0, 0, 0, 0, 0]:
        new_val = []
        for i, val in enumerate(update_diff):
            if 0 > old_val[i] + val or old_val[i] + val > _resource_card_pool[i]:
                print(f"BANK RES: illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
                return False
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            file.write(f"{new_val}".replace("[", "").replace("]", "").replace(" ", ""))
    return True


def get_bank_development_cards(repo: git.Repo):
    """
    Gets bank development cards from the file

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    development cards
    """
    path = os.path.join(repo.working_dir, "state", "game", "bank", "development_cards")
    development_cards = [0, 0, 0, 0, 0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            development_cards[i] = int(val)

    return development_cards


def update_bank_development_cards(repo: git.Repo, update_diff: [int]) -> bool:
    """
    Updates the banks resource cards and modifies the file


    Parameters
    ----------
    repo : current repo
    update_diff: card difference to be added (or subtracted)

    Returns
    -------
    success
    """
    if len(update_diff) != 5:
        print(f"illegal update length: {len(update_diff)} not 5")
        return False

    path = os.path.join(repo.working_dir, "state", "game", "bank", "development_cards")
    # load old value
    old_val = get_bank_development_cards(repo)

    # can only shrink
    for val in update_diff:
        if val > 0:
            print("illegal update: value above 0")
            return False

    if update_diff != [0, 0, 0, 0, 0]:
        new_val = []
        for i, val in enumerate(update_diff):
            if 0 > old_val[i] + val or old_val[i] + val > _development_card_pool[i]:
                print(f"BANK DEV CARDS: illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
                return False
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            file.write(f"{new_val}".replace("[", "").replace("]", "").replace(" ", ""))
    return True


def get_discard_pile(repo: git.Repo) -> [int]:
    """
    Gets the discard pile from the file

    Parameters
    ----------
    repo : current repo

    Returns
    -------
    discard pile
    """
    path = os.path.join(repo.working_dir, "state", "game", "discard_pile")
    pile = [0, 0, 0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            pile[i] = int(val)
    return pile


def update_discard_pile(repo: git.Repo, update_diff: [int]) -> bool:
    """
    Updates the discard pile and modifies the file

    Parameters
    ----------
    repo: current repo
    update_diff: card difference to be added (or subtracted)

    Returns
    -------
    success
    """
    path = os.path.join(repo.working_dir, "state", "game", "discard_pile")

    if len(update_diff) != 3:
        print(f"illegal update length: {len(update_diff)} not 3")
        return False
    # load old value
    old_val = get_discard_pile(repo)

    # can only grow
    for val in update_diff:
        if val < 0:
            print("illegal update: value below 0")
            return False

    if update_diff != [0, 0, 0]:
        new_val = []
        for i, val in enumerate(update_diff):
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            string = f"{new_val}".replace("[", "").replace("]", "").replace(" ", "")
            file.write(string)
    return True


# bandit
def get_bandit(repo: git.Repo, hexagons: [HexagonTile]) -> HexagonTile:
    """
    Gets the bandit's position from the file

    Parameters
    ----------
    repo : current repo
    hexagons: map tiles

    Returns
    -------
    bandit position
    """
    path = os.path.join(repo.working_dir, "state", "game", "bandit")
    with open(path, "r") as file:
        line = file.readline()
    return hexagons[int(line)]


def update_bandit(repo: git.Repo, hexagons: [HexagonTile], new_coords: int) -> bool:
    """
    Updates the bandit's position and modifies the file

    Parameters
    ----------
    repo : current repo
    hexagons: map tiles
    new_coords: index of the new map tile

    Returns
    -------
    success
    """
    path = os.path.join(repo.working_dir, "state", "game", "bandit")
    # load old value
    old_val = get_bandit(repo, hexagons)

    if old_val.id != new_coords:
        new_val = hexagons[new_coords]
        if new_val.resource == "Water":
            print(f"Illegal Bandit update: Tile: {new_coords}")
            return False
        else:
            with open(path, "w") as file:
                file.write(f"{new_coords}")
    return True


def get_all_settlement_points(repo: git.Repo, hexagons: [HexagonTile]) -> [Settlement_point]:
    """
    Gets all settlement points from file

    Parameters
    ----------
    repo : current repo
    hexagons: map tiles

    Returns
    -------
    settlement points
    """
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    settlement_points = []
    with open(path, "r") as file:
        for i, line in enumerate(file):
            line = line.split(",")
            settlement_points.append(
                Settlement_point(i, {hexagons[int(line[0])], hexagons[int(line[1])], hexagons[int(line[2])]}, line[3],
                                 line[4].replace("\n", "")))
    return settlement_points


def get_all_hexagon_tiles_with_nr(repo: git.Repo, hexagons: [HexagonTile], owner: str, roll: int) -> [HexagonTile]:
    """
    Returns all hexagon tiles with the given owner and dice number

    Parameters
    ----------
    repo : current repo
    hexagons: map tiles
    owner: player colour
    roll: number of the dice roll

    Returns
    -------
    map tiles
    """
    owner_index = owner.find("_")
    if owner_index != -1:
        owner = owner[:owner_index]

    settlement_points = get_all_settlement_points(repo, hexagons)
    bandit = get_bandit(repo, hexagons)
    viable = []
    for point in settlement_points:
        if point.owner == owner:
            for hexagon in point.coords:
                if hexagon.number == roll and bandit != hexagon:
                    viable.append(hexagon)

    return viable


def get_all_available_settlement_points(repo: git.Repo, settlement_points: [Settlement_point],
                                        hexagons: [HexagonTile]) -> [Settlement_point]:
    """
    Returns all settlement points that can still be built on according to the rules.

    Parameters
    ----------
    repo : current repo
    settlement_points: all settlement points
    hexagons: map tiles

    Returns
    -------
    available settlement points
    """
    available_settlement_points = []
    bandit = get_bandit(repo, hexagons)

    for point in settlement_points:
        # check for bandit
        if bandit in point.coords:
            continue
        if point.owner == "bot":
            # check that there are no other settlements neighbouring this point
            buildable = True

            for neighbour in settlement_points:
                if is_adjacent_settlement(point, neighbour) and neighbour.owner != "bot":
                    buildable = False
            if buildable:
                available_settlement_points.append(point)
    return available_settlement_points


def get_settlement_point(repo: git.Repo, index: int, hexagons: [HexagonTile]) -> Settlement_point:
    """
    Returns a specific settlement point given its index from the file as a settlement point

    Parameters
    ----------
    repo: current repo
    index: settlement point index

    Returns
    -------
    settlement point
    """
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
        line = line.split(",")

    return Settlement_point(index, {hexagons[int(line[0])], hexagons[int(line[1])], hexagons[int(line[2])]}, line[3],
                            line[4].replace("\n", ""))


def get_settlement_point_raw(repo: git.Repo, index: int) -> str:
    """
    Returns a specific settlement point given its index from the file as a string

    Parameters
    ----------
    repo: current repo
    index: settlement point index

    Returns
    -------
    settlement point data
    """
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
    return line


def update_settlement_point(repo: git.Repo, index: int, owner: str, settlement_type: str) -> bool:
    """
    Updates the settlement point given an index with a new owner and/or settlement type.

    Parameters
    ----------
    repo: current repo
    index: settlement point index
    owner: player colour
    settlement_type: Village or City

    Returns
    -------
    success
    """
    owner_index = owner.find("_")
    if owner_index != -1:
        owner = owner[:owner_index]

    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    raw_line = get_settlement_point_raw(repo, index)
    new_line = raw_line.replace("\n", "").split(",")
    new_line[3] = owner
    new_line[4] = settlement_type
    new_line = str.join(",", new_line)
    new_line += "\n"
    old_file = ""
    with open(path, "r") as f:
        old_file += f.read()

    old_file = old_file.replace(raw_line, new_line)

    with open(path, "w") as f:
        f.write(old_file)

    return True


def get_all_road_points(repo: git.Repo, hexagons: [HexagonTile]) -> [Road_point]:
    """
    Returns all road points from file

    Parameters
    ----------
    repo: current repo
    hexagons: map tiles

    Returns
    -------
    road points
    """
    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    road_points = []
    with open(path, "r") as file:
        for i, line in enumerate(file):
            line = line.split(",")
            road_points.append(
                Road_point(i, {hexagons[int(line[0])], hexagons[int(line[1])]}, line[2].replace("\n", "")))
    return road_points


def get_road_point(repo: git.Repo, index: int, hexagons: [HexagonTile]) -> Road_point:
    """
    Get a specific road point given its index from the file as a road point

    Parameters
    ----------
    repo: current repo
    index: road point index
    hexagons: map tiles

    Returns
    -------
    road point
    """
    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
        line = line.split(",")

    return Road_point(index, {hexagons[int(line[0])], hexagons[int(line[1])]}, line[2].replace("\n", ""))


def get_road_point_raw(repo: git.Repo, index: int) -> str:
    """
    Get a specific road point given its index from the file as a string

    Parameters
    ----------
    repo: current repo
    index: road point index

    Returns
    -------
    road point data
    """
    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
    return line


def get_all_available_road_points(repo: git.Repo, road_points: [Road_point], settlement_points: [Settlement_point],
                                  player_nr: int, hexagons: [HexagonTile]) -> [Road_point]:
    """
    Get all road points a specific player can build a road on, given the games rules.

    Parameters
    ----------
    repo: current repo
    road_points: all road points
    settlement_points: all settlement points
    player_nr: player number
    hexagons: map tiles

    Returns
    -------
    available road points
    """
    available_road_points = []

    for point in road_points:
        # check for bandit
        bandit = get_bandit(repo, hexagons)
        if bandit in point.coords:
            continue
        if point.owner == "bot":
            # check if there is a settlement adjacent to this road point
            for sp in settlement_points:
                if is_adjacent_road_to_settlement(sp, point) and sp.owner == get_player_colour(_number_of_players)[
                    player_nr]:
                    available_road_points.append(point)
                    break
    return available_road_points


def get_all_available_road_points_for_settlement(repo: git.Repo, road_points: [Road_point],
                                                 settlement_point: Settlement_point, player_nr: int,
                                                 hexagons: [HexagonTile]) -> [Road_point]:
    """
    Returns all road points that are adjacent to the given settlement point

    Parameters
    ----------
    repo: current repo
    road_points: all road points
    settlement_point: chosen settlement point
    player_nr: player number
    hexagons: map tiles

    Returns
    -------
    adjacent road points
    """
    available_road_points = []
    # check for bandit
    bandit = get_bandit(repo, hexagons)

    for point in road_points:
        if bandit in point.coords:
            continue
        if point.owner == "bot":
            # check if the settlement is adjacent to this road point
            if is_adjacent_road_to_settlement(settlement_point, point) and settlement_point.owner == \
                    get_player_colour(_number_of_players)[player_nr]:
                available_road_points.append(point)
    return available_road_points


def update_road_point(repo: git.Repo, index: int, owner: str) -> bool:
    """
    Updates the specified road point with the given index with the given owner

    Parameters
    ----------
    repo : current repo
    index: road point index
    owner: new owner

    Returns
    -------
    success
    """
    owner_index = owner.find("_")
    if owner_index != -1:
        owner = owner[:owner_index]

    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    raw_line = get_road_point_raw(repo, index)
    new_line = raw_line.replace("\n", "").split(",")
    new_line[2] = owner
    new_line = str.join(",", new_line)
    new_line += "\n"
    old_file = ""
    with open(path, "r") as f:
        old_file += f.read()

    old_file = old_file.replace(raw_line, new_line)

    with open(path, "w") as f:
        f.write(old_file)

    if new_line in old_file:
        return True
    else:
        return False


def is_adjacent_road_to_settlement(settlement_point: Settlement_point, road_point: Road_point) -> bool:
    """
    Computes if a road is adjacent to the given settlement point.

    Parameters
    ----------
    settlement_point: chosen settlement point
    road_point: chosen road point

    Returns
    -------
    is adjacent
    """
    tile_one = list(road_point.coords)[0]
    tile_two = list(road_point.coords)[1]

    if tile_one in settlement_point.coords and tile_two in settlement_point.coords:
        return True
    else:
        return False


def is_adjacent_settlement(settlement_point: Settlement_point, neighbour: Settlement_point) -> bool:
    """
    Computes if a settlement is adjacent to another settlement.

    Parameters
    ----------
    settlement_point: chosen settlement point
    neighbour: second chosen settlement point

    Returns
    -------
    is adjacent
    """
    tile_one = list(settlement_point.coords)[0]
    tile_two = list(settlement_point.coords)[1]
    tile_three = list(settlement_point.coords)[2]

    if tile_one in neighbour.coords and tile_two in neighbour.coords:
        return True
    elif tile_one in neighbour.coords and tile_three in neighbour.coords:
        return True
    elif tile_two in neighbour.coords and tile_three in neighbour.coords:
        return True
    else:
        return False


def create_git_dir(repo_folder: str) -> git.repo:
    """
    Creates a new git repository

    Parameters
    ----------
    repo_folder : context project list to display

    Returns
    -------
    git repo
    """
    catan = init_repo(ROOT_DIR, repo_folder, "alice", "alice@example.com", False)
    return catan


def create_git_dir_test() -> [git.repo]:
    """
    Creates a new git test repository


    Returns
    -------
    git repo
    """
    test = init_repo(TEST_DIR, "Catan_Test", "test", "test@example.com", False)

    return test


def get_resources_from_hextile(tiles: [HexagonTile]) -> [int]:
    """
    Returns the resources produced by the given hex tiles

    Parameters
    ----------
    tiles: map tiles

    Returns
    -------
    resource gains
    """
    resources = [0, 0, 0, 0, 0]

    for tile in tiles:
        if tile.resource == "Lumber":
            resources[0] += 1
        elif tile.resource == "Brick":
            resources[1] += 1
        elif tile.resource == "Wool":
            resources[2] += 1
        elif tile.resource == "Grain":
            resources[3] += 1
        elif tile.resource == "Ore":
            resources[4] += 1
    return resources


def get_player_reverse_index(colour: str) -> int:
    """
    Returns the reverse index of the given colour

    Parameters
    ----------
    colour: player colour

    Returns
    -------
    player number or -1 on failure
    """
    for i, player in enumerate(_player_colour_reversed_2_players[_number_of_players:]):
        if player == colour:
            return i
    return -1


def get_resources_from_dice_roll(repo: git.Repo, hexagons: [HexagonTile], roll: int, player_nr: int) -> [int]:
    """
    Computes all resources gained for a player given the dice result.

    Parameters
    ----------
    repo: current repo
    hexagons: map tiles
    roll: dice result
    player_nr: player number

    Returns
    -------
    resources gains
    """
    viable_hexagons = get_all_hexagon_tiles_with_nr(repo, hexagons, get_player_colour(_number_of_players)[player_nr],
                                                    roll)
    resources = get_resources_from_hextile(viable_hexagons)

    return resources


def get_sum_of_array(arr: [int]) -> int:
    """
    Sums the elements of an array

    Parameters
    ----------
    arr : array to sum

    Returns
    -------
    array sum
    """
    res_sum = 0
    for resource in arr:
        res_sum += resource
    return res_sum


def negate_int_arr(arr: [int]) -> [int]:
    """
    Negates all entries of an array.

    Parameters
    ----------
    arr: array to negate

    Returns
    -------
    negated array
    """
    for i, resource in enumerate(arr):
        arr[i] = -resource
    return arr


def randomly_choose_loss(loss, resources) -> [int]:
    """
    Given an amount of loss, choose the resource to lose.

    Parameters
    ----------
    loss: amount of cards the player has to lose

    Returns
    -------
    resource loss
    """
    diff = [0, 0, 0, 0, 0]
    i = 0
    # choose cards to loose
    while i < loss:
        index = randrange(0, 5)
        if resources[index] + diff[index] - 1 >= 0:
            diff[index] -= 1
            i += 1
    return diff


def get_diff_between_arrays(arr_1: [int], arr_2: [int]) -> [int]:
    """
    Computes the difference between two arrays

    Parameters
    ----------
    arr_1 : array
    arr_2 : array

    Returns
    -------
    array difference
    """
    if len(arr_1) != len(arr_2):
        print("Array length not equal")
        return
    else:
        diff = []
        for i in range(len(arr_1)):
            diff.append(arr_1[i] - arr_2[i])
        return diff


def get_all_settlements_of_player(settlement_points: [Settlement_point], player_nr: int) -> [Settlement_point]:
    """
    Filters the settlement points to only include the ones owned by the given player.

    Parameters
    ----------
    settlement_points: all settlement points
    player_nr: player number

    Returns
    -------
    player owned settlement points
    """
    owned = []
    for point in settlement_points:
        if point.owner == get_player_colour(_number_of_players)[player_nr]:
            owned.append(point)
    return owned


def get_all_roads_of_player(road_points: [Road_point], player_nr: int) -> [Road_point]:
    """
    Filters the road points to only include the ones owned by the given player.

    Parameters
    ----------
    road_points: all road points
    player_nr: player number

    Returns
    -------
    player owned road points
    """
    owned = []
    for point in road_points:
        if point.owner == get_player_colour(_number_of_players)[player_nr]:
            owned.append(point)
    return owned


def get_all_viable_settlement_points(settlement_points: [Settlement_point], road_points: [Road_point], player_nr: int,
                                     bandit: HexagonTile) -> [Settlement_point]:
    """
    Get all settlement points a specific player can place a village on, given the game's rules.

    Parameters
    ----------
    settlement_points: all settlement points
    road_points: all road points
    player_nr: player number
    bandit: bandit position

    Returns
    -------
    viable settlement points
    """
    owned_settlements = get_all_settlements_of_player(settlement_points, player_nr)
    owned_roads = get_all_roads_of_player(road_points, player_nr)

    owned_hexes = []

    # add all hexes with a village or road adjacent to it
    for point in owned_settlements:
        for coord in point.coords:
            if coord not in owned_hexes:
                owned_hexes.append(coord)
    for point in owned_roads:
        for coord in point.coords:
            if coord not in owned_hexes:
                owned_hexes.append(coord)

    available_settlement_points = []
    for point in settlement_points:
        # check for bandit
        if bandit in point.coords:
            continue
        # needs to be in one of the owned hexes
        for coord in point.coords:
            if coord not in owned_hexes:
                continue

        if point.owner == "bot":
            # check that there are no other settlements neighbouring this point
            buildable = True
            has_road = False
            for neighbour in settlement_points:
                if is_adjacent_settlement(point, neighbour) and neighbour.owner != "bot":
                    buildable = False
            # check if there is an adjacent road
            for road in owned_roads:
                if is_adjacent_road_to_settlement(point, road):
                    has_road = True
                    break
            if buildable and has_road:
                available_settlement_points.append(point)
    return available_settlement_points


def get_all_viable_road_points(settlement_points: [Settlement_point], road_points: [Road_point], player_nr: int,
                               bandit: HexagonTile) -> [Road_point]:
    """
    Get all road points a specific player can place a road on, given the game's rules.

    Parameters
    ----------
    settlement_points: all settlement points
    road_points: all road points
    player_nr: player number
    bandit: bandit position

    Returns
    -------
    viable road points
    """
    owned_settlements = get_all_settlements_of_player(settlement_points, player_nr)
    owned_roads = get_all_roads_of_player(road_points, player_nr)

    owned_hexes = []

    # add all hexes with a village or road adjacent to it
    for point in owned_settlements:
        for coord in point.coords:
            if coord not in owned_hexes:
                owned_hexes.append(coord)
    for point in owned_roads:
        for coord in point.coords:
            if coord not in owned_hexes:
                owned_hexes.append(coord)

    available_road_points = []
    for point in road_points:
        # check for bandit
        if bandit in point.coords:
            continue
        # needs to be in one of the owned hexes
        for coord in point.coords:
            if coord not in owned_hexes:
                continue

        if point.owner == "bot":
            sp_neighbour = []
            # get both adjacent settlement points
            for sp in settlement_points:
                if is_adjacent_road_to_settlement(sp, point):
                    sp_neighbour.append(sp)

            has_settlement = False
            has_road = False
            # check if there is an adjacent road
            for neighbour in owned_roads:
                for sp in sp_neighbour:
                    # neighbour road is adjacent to the same settlement point and the sp is not owned yet
                    if is_adjacent_road_to_settlement(sp, neighbour) and sp.owner == "bot":
                        has_road = True
            # check if there is an adjacent settlement of the player
            for settlement in owned_settlements:
                if has_road:
                    break
                if is_adjacent_road_to_settlement(settlement, point):
                    has_settlement = True
                    break
            if has_road or has_settlement:
                available_road_points.append(point)
    return available_road_points


def can_build_type(repo: git.Repo, resources: [int], building_type: str, player_nr: int) -> [bool]:
    """
    Check if a player can build a certain type of building, given the game's rules.

    Parameters
    ----------
    repo: current repo
    resources: list of player's resources
    building_type: type of building we want to check
    player_nr: player number

    Returns
    -------
    can build
    """
    can_build = True

    # check if the player has villages to spare
    available = get_player_buildings_type(repo, building_type, player_nr)
    if available == 0:
        can_build = False
        return can_build

    if building_type == "Village":
        cost = _cost_village
    elif building_type == "City":
        # check if there are villages to upgrade
        villages = get_player_buildings_type(repo, "Village", player_nr)
        if villages == 5:
            can_build = False
        cost = _cost_city
    elif building_type == "Road":
        cost = _cost_road
    else:
        cost = [20, 20, 20, 20, 20]

    for i in range(len(resources)):
        if resources[i] < cost[i]:
            can_build = False
            break
    return can_build


def can_buy_dev_card(repo: git.Repo, resources: [int]) -> [bool]:
    """
    Check if a player can buy a development card.

    Parameters
    ----------
    repo: current repo
    resources: list of player's resources

    Returns
    -------
    can buy
    """
    available_dev_cards = get_bank_development_cards(repo)
    cards = get_sum_of_array(available_dev_cards)
    can_buy = True
    for i in range(len(resources)):
        if resources[i] < _cost_dev_card[i]:
            can_buy = False
            break

    if cards == 0:
        can_buy = False

    return can_buy


def can_build_something(repo: git.Repo, resources: [int], local_player: int) -> bool:
    """
    Check if a player can build/buy anything

    Parameters
    ----------
    repo: current repo
    resources: list of player's resources
    local_player: player number

    Returns
    -------
    can build something
    """
    if (
            can_build_type(repo, resources, "City", local_player)
            or can_build_type(repo, resources, "Village", local_player)
            or can_build_type(repo, resources, "Road", local_player)
            or can_buy_dev_card(repo, resources)
    ):
        return True
    else:
        return False


def is_adjacent_road_to_road(settlement_points: [Settlement_point], point: Road_point, neighbour: Road_point) -> bool:
    """
    Check if a road is adjacent to another road.

    Parameters
    ----------
    settlement_points: all settlement points
    point: first road point
    neighbour: second road point

    Returns
    -------
    can build something
    """
    sp_neighbour = []
    # get both adjacent settlement points
    for sp in settlement_points:
        if is_adjacent_road_to_settlement(sp, point):
            sp_neighbour.append(sp)

    for sp in sp_neighbour:
        # neighbour road is adjacent to the same settlement point and not from an enemy settlement
        if is_adjacent_road_to_settlement(sp, neighbour) and (sp.owner == point.owner or sp.owner == "bot"):
            return True
    return False


def get_mightiest_army(repo: git.Repo, local_player: int) -> int:
    """
    Checks if the given player has the mightiest army.

    Parameters
    ----------
    repo: current repo
    local_player: player number

    Returns
    -------
    has mightiest army
    """
    uc = get_player_hand(repo, "unveiled_cards", local_player)
    knights = uc[0]
    largest_army = [0,0,0,0]

    # eligible for largest army
    for player in range(_number_of_players):
        player_uc = get_player_hand(repo, "unveiled_cards", player)
        largest_army[player] = player_uc[0]

    for player in range(_number_of_players):
        if largest_army[player] == max(largest_army) and largest_army[player] > 2:
            return player
    return -1


def get_longest_path(path_sum: int, road_start: Road_point, neighbours: [[Road_point]], visited: [Road_point], start_paths: [Road_point]):
    viable_neighbours = []
    max_path = 0
    if road_start not in visited:
        visited.append(road_start)

    for new_neighbour in neighbours[road_start.index]:
        # visit all adjacent roads
        if new_neighbour not in visited and new_neighbour not in start_paths:
            viable_neighbours.append(new_neighbour)

    if len(viable_neighbours) == 0:
        return path_sum + 1
    else:
        for neighbour in viable_neighbours:
            temp_sum = get_longest_path(path_sum, neighbour, neighbours, visited, viable_neighbours)
            if temp_sum >= max_path:
                max_path = temp_sum
    return path_sum + max_path + 1


def get_longest_road(repo: git.Repo, local_player: int, hexagons: [HexagonTile]) -> int:
    """
    Checks if the given player has the longest road. The longest road needs to be at least 5
    continuous pieces of road.

    Parameters
    ----------
    repo: current repo
    local_player: player number
    hexagons: map tiles

    Returns
    -------
    has longest road
    """
    sps = get_all_settlement_points(repo, hexagons)
    rps = get_all_road_points(repo, hexagons)

    longest_road = []
    for player in range(_number_of_players):
        longest_road.append([])
        roads = get_all_roads_of_player(rps, player)
        if local_player == player:
            if len(roads) < 5:
                return False
        else:
            if len(roads) < 5:
                longest_road[player] = 0
                continue
        neighbours = []
        # init list
        for _ in rps:
            neighbours.append([])
        # find all neighbours for all roads
        for road in roads:
            for neighbour in roads:
                if road.index == neighbour.index:
                    continue
                else:
                    if is_adjacent_road_to_road(sps, road, neighbour):
                        neighbours[road.index].append(neighbour)
        visited = []
        path_sum = [0, 0, 0, 0]
        index = 0

        while len(visited) != len(roads):
            # choose first roads to start (e.g. in case of split road networks)
            i = 0
            road = roads[0]
            while road in visited:
                road = roads[i]
                i += 1
            visited.append(road)

            start_paths = []
            for neighbour in neighbours[road.index]:
                # mark all initial neighbours as starter paths
                start_paths.append(neighbour)
            for neighbour in start_paths:
                # for all neighbours of the first road
                path_sum[index] = get_longest_path(0, neighbour, neighbours, visited, start_paths)
                index += 1

            if len(start_paths) == 0:
                return False
            elif len(start_paths) == 1:
                path_sum.sort(reverse=True)
                longest_road[player] = path_sum[0] + 1
            elif len(start_paths) == 2:
                path_sum.sort(reverse=True)
                # the starting road is not a middle piece between the paths
                if is_adjacent_road_to_road(sps, start_paths[0], start_paths[1]):
                    longest_road[player] = path_sum[0] + path_sum[1]
                else:
                    # the starting road is a middle piece
                    longest_road[player] = path_sum[0] + 1 + path_sum[1]
            elif len(start_paths) == 3:
                fst_val = 0
                fst_ind = 0
                snd_val = 0
                snd_ind = 0
                for val, i in enumerate(path_sum):
                    if val > fst_val:
                        fst_val = val
                        fst_ind = i
                    elif fst_val > 0 and val > snd_val:
                        snd_val = val
                        snd_ind = i

                # the starting road is not a middle piece between the paths
                if is_adjacent_road_to_road(sps, start_paths[fst_ind], start_paths[snd_ind]):
                    longest_road[player] = path_sum[fst_ind] + path_sum[snd_ind]
                else:
                    # the starting road is a middle piece
                    longest_road[player] = path_sum[fst_ind] + 1 + path_sum[snd_ind]
    for player in range(_number_of_players):
        if longest_road[player] == max(longest_road) and longest_road[player] >= 5:
            return player
    return -1


def count_points(repo: git.Repo, hexagons: [HexagonTile], local_player: int, longest_road: int,
                 mightiest_army: int) -> int:
    """
    Counts the victory points of a given player.

    Parameters
    ----------
    repo: current repo
    hexagons: map tiles
    local_player: player number
    longest_road: player with the longest road
    mightiest_army: player with the mightiest army

    Returns
    -------
    victory points
    """
    points = 0
    knights = 0
    roads = 0
    villages = 0
    cities = 0
    vp = 0

    uc = get_player_hand(repo, "unveiled_cards", local_player)
    vp += uc[1]

    sps = get_all_settlement_points(repo, hexagons)
    settlements = get_all_settlements_of_player(sps, local_player)

    for settlement in settlements:
        if settlement.type == "Village":
            villages += 1
        elif settlement.type == "City":
            cities += 2

    if local_player == longest_road:
        roads += 2

    if local_player == mightiest_army:
        knights += 2

    points = vp + knights + roads + villages + cities
    if points >= 8:
        print(f"{get_player_colour(_number_of_players)[local_player]}_{points}: villages: {villages} | cities: {cities} | vp: {vp} | longest road: {roads} | mightiest army: {knights} ")
    return points


def get_all_viable_bandit_positions(repo: git.Repo, hexagons: [HexagonTile], local_player: int) -> [HexagonTile]:
    """
    Returns all possible bandit positions that do not border a building of a given player.

    Parameters
    ----------
    repo : current repo
    hexagons: map tiles
    local_player: player number

    Returns
    -------
    viable bandit positions
    """
    player_hexes = []
    sps = get_all_settlement_points(repo, hexagons)
    rps = get_all_road_points(repo, hexagons)

    settlements = get_all_settlements_of_player(sps, local_player)
    roads = get_all_roads_of_player(rps, local_player)

    # gather all hexes that have player buildings on them
    for settlement in settlements:
        for coord in settlement.coords:
            if coord not in player_hexes:
                player_hexes.append(coord)
    for road in roads:
        for coord in road.coords:
            if coord not in player_hexes:
                player_hexes.append(coord)

    viable_bandit_positions = []

    for hex in hexagons:
        if hex in player_hexes:
            continue
        else:
            if hex.resource != "Water":
                viable_bandit_positions.append(hex)

    return viable_bandit_positions


def get_settlements_adjacent_to_tile(repo: git.Repo, hexagons: [HexagonTile], hexagon: HexagonTile) -> [
    Settlement_point]:
    """
    Gets all settlements adjacent to a given tile.

    Parameters
    ----------
    repo : current repo
    hexagons: map tiles
    hexagon: given map tile

    Returns
    -------
    settlement points adjacent to tile
    """
    sps = get_all_settlement_points(repo, hexagons)
    settlements = []

    for sp in sps:
        if sp.owner != "bot" and hexagon in sp.coords:
            settlements.append(sp)

    return settlements
