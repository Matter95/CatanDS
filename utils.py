import os
from typing import Tuple, List

import git
from git import Git

from gloabl_definitions import MapTile, Settlement_point, Map, HexagonTile, Road_point, _player_colour


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
    if current_phase == "dice_roll":
        return "trading"
    elif current_phase == "trading":
        return "building"
    elif current_phase == "building":
        return "dice_roll"
    else:
        return ""



def get_wharf_type(settlement: Settlement_point):
    pass
def get_initial_phase(repo: git.Repo):
    try:
        with open(os.path.join(repo.working_dir, "state", "initialization", "init_phase"), "r") as file:
            line = file.readline()
        return line
    except FileNotFoundError:
        return None

def get_initial_active_player(repo: git.Repo):
    with open(os.path.join(repo.working_dir, "state", "initialization", "active_player"), "r") as file:
        line = file.readline()
    return line

def get_active_player(repo: git.Repo):
    with open(os.path.join(repo.working_dir, "state", "game", "active_player"), "r") as file:
        line = file.readline()
    return line

def get_turn_phase(repo: git.Repo):
    with open(os.path.join(repo.working_dir, "state", "game", "turn_phase"), "r") as file:
        line = file.readline()
    return line

# player functions
def get_player_hand(repo: git.Repo, hand_type: str, player_nr: int) -> List[int] | None:
    path = os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{player_nr}")

    if hand_type == "resource_cards":
        vals = [0, 0, 0, 0, 0]
        path = os.path.join(path, "resource_cards")
    elif hand_type == "bought_cards":
        vals = [0, 0, 0, 0, 0]
        path = os.path.join(path, "bought_cards")
    elif hand_type == "available_cards":
        vals = [0, 0, 0]
        path = os.path.join(path, "available_cards")
    elif hand_type == "unveiled_cards":
        vals = [0, 0]
        path = os.path.join(path, "unveiled_cards")
    else:
        return None

    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")

        for i, v in enumerate(line):
            vals[i] = int(v)

    return vals

def update_player_hand(repo: git.Repo, player_nr: int, hand_type: str, update_diff: Tuple[int, ...]):
    pass

def get_player_unveiled_cards(repo: git.Repo, player_nr: int):
    pass

def update_player_unveiled_cards(repo: git.Repo, player_nr: int, update_diff: Tuple[int, ...]):
    pass

def get_player_buildings(repo: git.Repo, building_type: str, player_nr: int) -> int | None:
    path = os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{player_nr}")

    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        if building_type == "road":
            line = line[0]
        elif building_type == "village":
            line = line[1]
        elif building_type == "city":
            line = line[2]
        else:
            return None

    return int(line)

def update_player_buildings(repo: git.Repo, player_nr: int,  building_type: str, diff: int):
    pass

# bank functions
def get_bank_resources(repo: git.Repo):
    path = os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards")
    resource_cards = [0,0,0,0,0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            resource_cards[i] = int(val)

    return resource_cards

def update_bank_resources(repo: git.Repo, update_diff: Tuple[int, ...]):
    pass

def get_bank_development_cards(repo: git.Repo):
    path = os.path.join(repo.working_dir, "state", "game", "bank", "development_cards")
    development_cards = [0, 0, 0, 0, 0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            development_cards[i] = int(val)

    return development_cards

def update_bank_development_cards(repo: git.Repo, update_diff: Tuple[int, ...]):
    pass

def get_discard_pile(repo: git.Repo):
    path = os.path.join(repo.working_dir, "state", "game", "discard_pile")
    pile = [0, 0, 0]
    with open(path, "r") as file:
        line = file.readline()
        line = line.split(",")
        for i, val in enumerate(line):
            pile[i] = int(val)

    return pile

def update_discard_pile(repo: git.Repo, update_diff: Tuple[int, ...]):
    pass

# bandit
def get_bandit(repo: git.Repo):
    path = os.path.join(repo.working_dir, "state", "game", "bandit")
    with open(path, "r") as file:
        line = file.readline()
    return int(line)

def update_bandit(repo: git.Repo, coords: MapTile):
    pass

def get_all_settlement_points(repo: git.Repo, hexagons: [HexagonTile]) -> [Settlement_point]:
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    settlement_points = []
    with open(path, "r") as file:
        for i, line in enumerate(file):
            line = line.split(",")
            settlement_points.append(Settlement_point({hexagons[int(line[0])], hexagons[int(line[1])], hexagons[int(line[2])]}, line[3], line[4].replace("\n","")))
    return settlement_points

def get_settlement_point(repo: git.Repo, index: int, hexagons: [HexagonTile]):
    path = os.path.join(repo.working_dir, "state", "game", "settlement_points")
    with open(path, "r") as file:
        for i in range(index + 1):
            line = file.readline()
        line = line.split(",")

    return Settlement_point({hexagons[int(line[0])], hexagons[int(line[1])], hexagons[int(line[2])]}, line[3], line[4].replace("\n",""))

def update_settlement_point(repo: git.Repo, index: int, owner: str, settlement_type: str):
    pass

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


def get_all_available_road_points(repo: git.Repo, road_points: [Road_point], settlement_points: [Settlement_point], player_nr: int) -> [Road_point]:
    available_road_points = []

    for point in road_points:
        if point.owner == "bot":
            for sp in settlement_points:
                if is_adjacent_road_to_settlement(sp, point) and owned_by_player(sp, _player_colour[player_nr]):
                    available_road_points.append(point)
                    break
    return available_road_points



def update_road_point(repo: git.Repo, index: int, owner: str):
    pass


def owned_by_player(settlement_point: Settlement_point, owner: str):
    if settlement_point.owner == owner:
        return True
    else:
        return False

def is_adjacent_road_to_settlement(settlement_point: Settlement_point, road_point: Road_point) -> bool:
    for tile_one in settlement_point.coords:
        for tile_two in settlement_point.coords:
            if tile_one.__eq__(tile_two):
                continue
            if tile_one in road_point.coords and tile_two in road_point.coords:
                return True
    return False


