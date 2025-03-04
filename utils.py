import os
from typing import Tuple

from git import Git

from gloabl_definitions import Map, MapTile, Settlement_point, Road_point


def create_folder_structure(repo: Git.Repo, n_players: int):

    folders = [
        "state",
        os.path.join("state", "game"),
        os.path.join("state", "game", "bank"),
        os.path.join("state", "game", "player_hands"),
        os.path.join("state", "game", "player_buildings"),
        os.path.join("state", "initialization"),
    ]

    for i in range(n_players):
        folders += [
            os.path.join("state", "game", "player_hands", f"player_{i + 1}"),
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


def get_settlement_points() -> [Settlement_point]:
    used_coordinates: {Tuple[MapTile, ...]} = set()
    settlement_points: [Settlement_point] = []
    for i, t1 in enumerate(Map):
        for j, t2 in enumerate(Map):
            if i == j:
                continue
            for k, t3 in enumerate(Map):
                if i == k or j == k:
                    continue
                if (t1, t2, t3) not in used_coordinates:
                    used_coordinates.add((t1, t2, t3))
                    settlement_points.append(
                        Settlement_point(
                            f"{t1.designation}{t2.designation}{t3.designation}",
                            (t1, t2, t3),
                            "bot",
                            "bot"
                        )
                    )
    return settlement_points

def get_road_points():
    used_coordinates: {Tuple[MapTile, MapTile]} = set()
    road_points: [Settlement_point] = []
    for i, t1 in enumerate(Map):
        for j, t2 in enumerate(Map):
            if i == j:
                continue
            if (t1, t2) not in used_coordinates:
                used_coordinates.add((t1, t2))
                road_points.append(
                    Road_point(
                        f"{t1.designation}{t2.designation}",
                        (t1, t2),
                        "bot",
                    )
                )
    return road_points