import os

import git
import numpy as np
from git import Git



def create_folder_structure(repo: git.Repo, n_players: int):

    folders = [
        "state",
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

def angle_between(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return np.rad2deg((ang1 - ang2) % (2 * np.pi))