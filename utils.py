import os
from random import randrange
from typing import List

import git

from gloabl_definitions import (
    Settlement_point,
    HexagonTile,
    Road_point,
    _player_colour_2_players,
    ROOT_DIR,
    REMOTE_DIR,
    _resource_card_pool,
    _number_of_players,
    _development_card_pool,
    _player_building_pool,
    TEST_DIR, _player_colour_reversed_2_players, _cost_village, _cost_city, _cost_road, _cost_dev_card,
)
from repo_utils import init_repo


def create_folder_structure(repo: git.Repo, n_players: int):

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
    if current_phase == "phase_one":
        return "phase_two"
    elif current_phase == "phase_two":
        return "phase_two"
    else:
        return ""

def turn_phase_next(current_phase: str) -> str:
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



def get_wharf_type(settlement: Settlement_point):
    pass

# getter and setter for the files
def get_initial_phase(repo: git.Repo):
    try:
        with open(os.path.join(repo.working_dir, "state", "initialization", "init_phase"), "r") as file:
            line = file.readline()
        return line
    except FileNotFoundError:
        return None

def update_initial_phase(repo: git.Repo):
    # load old value
    old_val = get_initial_phase(repo)
    # get next phase
    new_val = init_phase_next(old_val)

    with open(os.path.join(repo.working_dir, "state", "initialization", "init_phase"), "w") as file:
        file.write(f"{new_val}")

def get_initial_active_player(repo: git.Repo):
    with open(os.path.join(repo.working_dir, "state", "initialization", "active_player"), "r") as file:
        line = file.readline()
    return int(line)

def get_player_index(colour: str):
    for i, c in enumerate(_player_colour_2_players):
        if c == colour:
            return i

def update_initial_active_player(repo: git.Repo):
    old_val = int(get_initial_active_player(repo))

    new_val = (old_val + 1) % _number_of_players

    with open(os.path.join(repo.working_dir, "state", "initialization", "active_player"), "w") as file:
        file.write(f"{new_val}")

def update_initial_active_player_rev(repo: git.Repo):
    old_val = int(get_initial_active_player(repo))

    new_val = (old_val - 1) % _number_of_players

    with open(os.path.join(repo.working_dir, "state", "initialization", "active_player"), "w") as file:
        file.write(f"{new_val}")

def get_active_player(repo: git.Repo):
    with open(os.path.join(repo.working_dir, "state", "game", "active_player"), "r") as file:
        line = file.readline()
    return int(line)

def update_active_player(repo: git.Repo):
    old_val = get_active_player(repo)

    new_val = (old_val + 1) % _number_of_players

    with open(os.path.join(repo.working_dir, "state", "game", "active_player"), "w") as file:
        file.write(f"{new_val}")


def get_turn_phase(repo: git.Repo):
    with open(os.path.join(repo.working_dir, "state", "game", "turn_phase"), "r") as file:
        line = file.readline()
    return line

def update_turn_phase(repo: git.Repo, win: bool = False):
    # load old value
    old_val = get_turn_phase(repo)
    # get next phase
    new_val = turn_phase_next(old_val)

    if win:
        new_val = "top"

    with open(os.path.join(repo.working_dir, "state", "game", "turn_phase"), "w") as file:
        file.write(f"{new_val}")


# player functions
def get_player_hand(repo: git.Repo, hand_type: str, player_nr: int) -> List[int] | None:
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

    with open(os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_nr + 1}", hand_type), "r") as file:
        line = file.readline()
        line = line.split(",")

        for i, val in enumerate(line):
            vals[i] = int(val)

    return vals

def update_player_hand(repo: git.Repo, hand_type: str, player_nr: int, update_diff: [int]):
    path = os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_nr + 1}")

    old_val = get_player_hand(repo, hand_type, player_nr)

    if hand_type == "resource_cards":
        empty = [0, 0, 0, 0, 0]
        path = os.path.join(path, "resource_cards")
    elif hand_type == "bought_cards":
        empty = [0, 0, 0, 0, 0]
        path = os.path.join(path, "bought_cards")
    elif hand_type == "available_cards":
        empty = [0, 0, 0, 0]
        path = os.path.join(path, "available_cards")
    elif hand_type == "unveiled_cards":
        empty = [0, 0]
        path = os.path.join(path, "unveiled_cards")
    else:
        print(f"illegal hand_type: {hand_type}")
        return

    if update_diff != empty:
        new_val = []
        for i, val in enumerate(update_diff):
            if hand_type == "resource_cards":
                if 0 > old_val[i] + val or old_val[i] + val  > _resource_card_pool[i]:
                    print(f"illegal update: Available {old_val[i]}, add {update_diff[i]}, max {_resource_card_pool[i]}")
                    return
            else:
                j = i
                if hand_type == "unveiled_cards":
                    j += 3
                if 0 > old_val[i] + val or old_val[i] + val > _development_card_pool[j]:
                    print(
                        f"illegal update: Available {old_val[i]}, add {update_diff[i]}, max {_resource_card_pool[i]}")
                    return
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            file.write(f"{new_val}".replace("[", "").replace("]", "").replace(" ", ""))


def get_player_buildings(repo: git.Repo, player_nr: int) -> [int]:
    path = os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{player_nr + 1}")
    buildings: [int] = []
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for element in line:
            buildings.append(int(element))
    return buildings

def get_player_buildings_type(repo: git.Repo, building_type: str, player_nr: int) -> int | None:
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

def update_player_buildings(repo: git.Repo, player_nr: int, update_diff: [int]):
    path = os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{player_nr + 1}")

    old_val = get_player_buildings(repo, player_nr)

    if update_diff != [0, 0, 0]:
        new_val = []
        for i, val in enumerate(update_diff):
            if 0 > old_val[i] + val or old_val[i] + val > _player_building_pool[i]:
                print(f"PLAYER BUILDING: illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
                return
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            file.write(f"{new_val}".replace("[", "").replace("]", "").replace(" ", ""))

# bank functions
def get_bank_resources(repo: git.Repo):
    path = os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards")
    resource_cards = [0, 0, 0, 0, 0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            resource_cards[i] = int(val)

    return resource_cards

def update_bank_resources(repo: git.Repo, update_diff: [int]):
    if len(update_diff) != 5:
        print(f"illegal update length: {len(update_diff)} not 5")
        return

    path = os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards")
    # load old value
    old_val = get_bank_resources(repo)

    if update_diff != [0, 0, 0, 0, 0]:
        new_val = []
        for i, val in enumerate(update_diff):
            if 0 > old_val[i] + val or old_val[i] + val > _resource_card_pool[i]:
                print(f"BANK RES: illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
                return
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            file.write(f"{new_val}".replace("[", "").replace("]", "").replace(" ", ""))


def get_bank_development_cards(repo: git.Repo):
    path = os.path.join(repo.working_dir, "state", "game", "bank", "development_cards")
    development_cards = [0, 0, 0, 0, 0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            development_cards[i] = int(val)

    return development_cards

def update_bank_development_cards(repo: git.Repo, update_diff: [int]):
    if len(update_diff) != 5:
        print(f"illegal update length: {len(update_diff)} not 5")
        return

    path = os.path.join(repo.working_dir, "state", "game", "bank", "development_cards")
    # load old value
    old_val = get_bank_development_cards(repo)

    # can only shrink
    for val in update_diff:
        if val > 0:
            print("illegal update: value above 0")
            return

    if update_diff != [0, 0, 0, 0, 0]:
        new_val = []
        for i, val in enumerate(update_diff):
            if 0 > old_val[i] + val or old_val[i] + val > _development_card_pool[i]:
                print(f"BANK DEV CARDS: illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
                return
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            file.write(f"{new_val}".replace("[", "").replace("]", "").replace(" ", ""))

def get_discard_pile(repo: git.Repo):
    path = os.path.join(repo.working_dir, "state", "game", "discard_pile")
    pile = [0, 0, 0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            pile[i] = int(val)
    return pile

def update_discard_pile(repo: git.Repo, update_diff: [int]):
    path = os.path.join(repo.working_dir, "state", "game", "discard_pile")

    if len(update_diff) != 3:
        print(f"illegal update length: {len(update_diff)} not 3")
        return
    # load old value
    old_val = get_discard_pile(repo)

    # can only grow
    for val in update_diff:
        if val < 0:
            print("illegal update: value below 0")
            return

    if update_diff != [0, 0, 0]:
        new_val = []
        for i, val in enumerate(update_diff):
            new_val.append(old_val[i] + val)
        with open(path, "w") as file:
            string = f"{new_val}".replace("[", "").replace("]", "").replace(" ", "")
            file.write(string)

# bandit
def get_bandit(repo: git.Repo, hexagons: [HexagonTile]) -> HexagonTile:
    path = os.path.join(repo.working_dir, "state", "game", "bandit")
    with open(path, "r") as file:
        line = file.readline()
    return hexagons[int(line)]

def update_bandit(repo: git.Repo, hexagons: [HexagonTile], new_coords: int):
    path = os.path.join(repo.working_dir, "state", "game", "bandit")
    # load old value
    old_val = get_bandit(repo, hexagons)

    if old_val.id != new_coords:
        new_val = hexagons[new_coords]
        if new_val.resource == "Water":
            print(f"Illegal Bandit update: Tile: {new_coords}")
        else:
            with open(path, "w") as file:
                file.write(f"{new_coords}")


def get_all_settlement_points(repo: git.Repo, hexagons: [HexagonTile]) -> [Settlement_point]:
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    settlement_points = []
    with open(path, "r") as file:
        for i, line in enumerate(file):
            line = line.split(",")
            settlement_points.append(Settlement_point(i, {hexagons[int(line[0])], hexagons[int(line[1])], hexagons[int(line[2])]}, line[3], line[4].replace("\n","")))
    return settlement_points

def get_all_hexagon_tiles_with_nr(repo: git.Repo, hexagons: [HexagonTile], owner: str, roll: int) -> [HexagonTile]:
    settlement_points = get_all_settlement_points(repo, hexagons)
    bandit = get_bandit(repo, hexagons)
    viable = []
    for point in settlement_points:
        if point.owner == owner:
            for hexagon in point.coords:
                if hexagon.number == roll and bandit != hexagon:
                    viable.append(hexagon)

    return viable


def get_all_available_settlement_points(repo: git.Repo, settlement_points: [Settlement_point], hexagons: [HexagonTile]) -> [Settlement_point]:
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

def get_settlement_point(repo: git.Repo, index: int, hexagons: [HexagonTile]):
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
        line = line.split(",")

    return Settlement_point(index, {hexagons[int(line[0])], hexagons[int(line[1])], hexagons[int(line[2])]}, line[3], line[4].replace("\n",""))

def get_settlement_point_raw(repo: git.Repo, index: int):
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
    return line

def update_settlement_point(repo: git.Repo, index: int, owner: str, settlement_type: str):
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    raw_line = get_settlement_point_raw(repo, index)
    new_line = raw_line.replace("\n","").split(",")
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


def get_all_road_points(repo: git.Repo, hexagons: [HexagonTile]) -> [Road_point]:
    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    road_points = []
    with open(path, "r") as file:
        for i, line in enumerate(file):
            line = line.split(",")
            road_points.append(Road_point(i, {hexagons[int(line[0])], hexagons[int(line[1])]}, line[2].replace("\n","")))
    return road_points

def get_road_point(repo: git.Repo, index: int, hexagons: [HexagonTile]):
    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
        line = line.split(",")

    return Road_point(index, {hexagons[int(line[0])], hexagons[int(line[1])]}, line[2].replace("\n",""))


def get_road_point_raw(repo: git.Repo, index: int) -> str:
    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()

    return line

def get_all_available_road_points(repo: git.Repo, road_points: [Road_point], settlement_points: [Settlement_point], player_nr: int, hexagons: [HexagonTile]) -> [Road_point]:
    available_road_points = []

    for point in road_points:
        # check for bandit
        bandit = get_bandit(repo, hexagons)
        if bandit in point.coords:
            continue
        if point.owner == "bot":
            # check if there is a settlement adjacent to this road point
            for sp in settlement_points:
                if is_adjacent_road_to_settlement(sp, point) and sp.owner == _player_colour_2_players[player_nr]:
                    available_road_points.append(point)
                    break
    return available_road_points

def get_all_available_road_points_for_settlement(repo: git.Repo, road_points: [Road_point], settlement_point: Settlement_point, player_nr: int, hexagons: [HexagonTile]) -> [Road_point]:
    available_road_points = []
    # check for bandit
    bandit = get_bandit(repo, hexagons)

    for point in road_points:
        if bandit in point.coords:
            continue
        if point.owner == "bot":
            # check if the settlement is adjacent to this road point
            if is_adjacent_road_to_settlement(settlement_point, point) and settlement_point.owner == _player_colour_2_players[player_nr]:
                available_road_points.append(point)
    return available_road_points


def update_road_point(repo: git.Repo, index: int, owner: str):
    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    raw_line = get_road_point_raw(repo, index)
    new_line = raw_line.replace("\n","").split(",")
    new_line[2] = owner
    new_line = str.join(",", new_line)
    new_line += "\n"
    old_file = ""
    with open(path, "r") as f:
        old_file += f.read()

    old_file = old_file.replace(raw_line, new_line)

    with open(path, "w") as f:
        f.write(old_file)

def is_adjacent_road_to_settlement(settlement_point: Settlement_point, road_point: Road_point) -> bool:
    tile_one = list(road_point.coords)[0]
    tile_two = list(road_point.coords)[1]

    if tile_one in settlement_point.coords and tile_two in settlement_point.coords:
        return True
    else:
        return False


def is_adjacent_settlement(settlement_point: Settlement_point, neighbour: Settlement_point) -> bool:
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


def create_git_dir() -> git.repo:
    alice = init_repo(ROOT_DIR, "Catan", "alice", "alice@example.com", False)
    return alice


def create_git_dir_test() -> [git.repo]:
    test = init_repo(TEST_DIR, "Catan_Test", "test", "test@example.com", False)

    return test


def get_settlement_point_index(sp: Settlement_point, settlement_points: [Settlement_point]) -> int:
    for i, point in enumerate(settlement_points):
        if sp.coords == point.coords:
            return i
    return -1

def get_road_point_index(rp: Road_point, road_points: [Road_point]) -> int:
    for i, point in enumerate(road_points):
        if rp.coords == point.coords:
            return i
    return -1

def get_resources_from_hextile(tiles: [HexagonTile]) -> [int]:
    resources = [0,0,0,0,0]

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
    for i, player in enumerate(_player_colour_reversed_2_players[_number_of_players:]):
        if player == colour:
            return i
    return -1

def get_resources_from_dice_roll(repo: git.Repo, hexagons: [HexagonTile], roll: int, player_nr: int) -> [int]:
    viable_hexagons = get_all_hexagon_tiles_with_nr(repo, hexagons, repo.active_branch.name, roll)
    resources = get_resources_from_hextile(viable_hexagons)

    return resources

def get_sum_of_array(arr: [int]) -> int:
    res_sum = 0
    for resource in arr:
        res_sum += resource
    return res_sum

def negate_int_arr(resources: [int]) -> [int]:
    for i, resource in enumerate(resources):
        resources[i] = -resource
    return resources

def randomly_choose_loss(loss, resources):
    diff = [0, 0, 0, 0, 0]
    i = 0
    # choose cards to loose
    while i < loss:
        index = randrange(0, 5)
        if resources[index] + diff[index] - 1 >= 0:
            diff[index] -= 1
            i += 1
    return diff


def get_diff_between_arrays(arr_1: [int], arr_2: [int]):
    if len(arr_1) != len(arr_2):
        print("Array length not equal")
        return
    else:
        diff = []
        for i in range(len(arr_1)):
            diff.append(arr_1[i] - arr_2[i])
        return diff

def get_all_settlements_of_player(settlement_points: [Settlement_point], player_nr: int) -> [Settlement_point]:
    owned = []
    for point in settlement_points:
        if point.owner == _player_colour_2_players[player_nr]:
            owned.append(point)
    return owned


def get_all_roads_of_player(road_points: [Road_point], player_nr: int) -> [Road_point]:
    owned = []
    for point in road_points:
        if point.owner == _player_colour_2_players[player_nr]:
            owned.append(point)
    return owned


def get_all_viable_settlement_points(settlement_points: [Settlement_point], road_points: [Road_point], player_nr: int, bandit: HexagonTile) -> [Settlement_point]:
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


def get_all_viable_road_points(settlement_points: [Settlement_point], road_points: [Road_point], player_nr: int, bandit: HexagonTile) -> [Road_point]:
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

            # check that there are no other settlements neighbouring this point
            has_settlement = False
            has_road = False
            for neighbour in owned_roads:
                for sp in sp_neighbour:
                    # neighbour road is adjacent to the same settlement point
                    if is_adjacent_road_to_settlement(sp, neighbour) and neighbour.owner == _player_colour_2_players[player_nr]:
                        has_road = True
            # check if there is an adjacent road
            for settlement in owned_settlements:
                if has_road:
                    break
                if is_adjacent_road_to_settlement(settlement, point):
                    has_settlement = True
                    break
            if has_road or has_settlement:
                available_road_points.append(point)
    return available_road_points


def can_build_type(repo, resources: [int], building_type: str, player_nr: int) -> [bool]:
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
        cost = [20,20,20,20,20]

    for i in range(len(resources)):
        if resources[i] < cost[i]:
            can_build = False
            break
    return can_build


def can_buy_dev_card(repo: git.Repo, resources: [int]) -> [bool]:
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
    if (
        can_build_type(repo, resources, "City", local_player)
        or can_build_type(repo, resources, "Village", local_player)
        or can_build_type(repo, resources, "Road", local_player)
        or can_buy_dev_card(repo, resources)
    ):
        return True
    else:
        return False


def count_points(repo: git.Repo, hexagons: [HexagonTile], local_player: int) -> int:
    points = 0

    uc = get_player_hand(repo, "unveiled_cards", local_player)
    knights = uc[0]
    vp = uc[1]

    #eligible for largest army
    if knights > 3:
        largest_army = True
        for player in range(_number_of_players):
            if player != local_player:
                player_uc = get_player_hand(repo, "unveiled_cards", player)
                if knights < player_uc[0]:
                    largest_army = False
        if largest_army:
            points += 2

    points += vp

    sps = get_all_settlement_points(repo, hexagons)
    settlements = get_all_settlements_of_player(sps, local_player)

    for settlement in settlements:
        if settlement.type == "Village":
            points += 1
        elif settlement.type == "City":
            points += 2
    return points

def get_all_viable_bandit_positions(repo: git.Repo, hexagons: [HexagonTile], local_player: int) -> [HexagonTile]:
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

def get_settlements_adjacent_to_tile(repo: git.Repo, hexagons: [HexagonTile], hexagon: HexagonTile) -> [Settlement_point]:
    sps = get_all_settlement_points(repo, hexagons)
    settlements = []

    for sp in sps:
        if sp.owner != "bot" and hexagon in sp.coords:
            settlements.append(sp)

    return settlements