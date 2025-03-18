import os
from typing import List

import git

from gloabl_definitions import (
    Settlement_point,
    HexagonTile,
    Road_point,
    _player_colour,
    ROOT_DIR,
    REMOTE_DIR,
    _resource_card_pool,
    _number_of_players,
    _development_card_pool,
    _player_building_pool,
    TEST_DIR, _player_colour_reversed,
)
from repo_utils import init_repo, get_repo_author_gitdir


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

def update_turn_phase(repo: git.Repo):
    # load old value
    old_val = get_turn_phase(repo)
    # get next phase
    new_val = turn_phase_next(old_val)

    with open(os.path.join(repo.working_dir, "state", "game", "turn_phase"), "w") as file:
        file.write(f"{new_val}")


# player functions
def get_player_hand(repo: git.Repo, hand_type: str, player_nr: int) -> List[int] | None:


    if hand_type == "resource_cards":
        vals = [0, 0, 0, 0, 0]
    elif hand_type == "bought_cards":
        vals = [0, 0, 0, 0, 0]
    elif hand_type == "available_cards":
        vals = [0, 0, 0]
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
        empty = [0, 0, 0]
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
                print(f"illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
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
                print(f"illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
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
            if 0 > old_val[i] + val <= _development_card_pool[i]:
                print(f"illegal update: not enough cards. Available {old_val[i]}, decrease {val}")
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
            settlement_points.append(Settlement_point({hexagons[int(line[0])], hexagons[int(line[1])], hexagons[int(line[2])]}, line[3], line[4].replace("\n","")))
    return settlement_points


def get_all_available_settlement_points(repo: git.Repo, settlement_points: [Settlement_point], player_nr: int, hexagons: [HexagonTile]) -> [Road_point]:
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

    return Settlement_point({hexagons[int(line[0])], hexagons[int(line[1])], hexagons[int(line[2])]}, line[3], line[4].replace("\n",""))

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
            road_points.append(Road_point({hexagons[int(line[0])], hexagons[int(line[1])]}, line[2].replace("\n","")))
    return road_points

def get_road_point(repo: git.Repo, index: int, hexagons: [HexagonTile]):
    path = os.path.join(repo.working_dir, "state", "game", "road_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
        line = line.split(",")

    return Road_point({hexagons[int(line[0])], hexagons[int(line[1])]}, line[2].replace("\n",""))


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
                if is_adjacent_road_to_settlement(sp, point) and sp.owner == _player_colour[player_nr]:
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
            if is_adjacent_road_to_settlement(settlement_point, point) and settlement_point.owner == _player_colour[player_nr]:
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


def create_git_dirs() -> [git.repo]:
    alice = init_repo(ROOT_DIR, "Catan_Alice", "alice", "alice@example.com", False)
    bob = init_repo(REMOTE_DIR, "Catan_Bob", "bob", "bob@example.com", False)

    name = get_repo_author_gitdir(bob.git_dir)
    alice.create_remote(name, bob.git_dir)
    print(f"created Remote {name} for {get_repo_author_gitdir(alice.git_dir)}")

    name = get_repo_author_gitdir(alice.git_dir)
    bob.create_remote(name, alice.git_dir)
    print(f"created Remote {name} for {get_repo_author_gitdir(bob.git_dir)}")
    return alice, bob


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
    for i, player in enumerate(_player_colour_reversed[_number_of_players:]):
        if player == colour:
            return i
    return -1