import os
from typing import List

import git
from gloabl_definitions import _resource_card_pool, _development_card_pool, Settlement_point, Road_point
from utils import create_folder_structure


def initialize_game_state(
    repo: git.Repo,
    settlement_points: [Settlement_point],
    road_points: [Road_point],
) -> git.Commit:
    """
    Initializes the game and initialization state.

    Parameters
    ----------
    repo : working repository

    Returns
    -------
    initial git Commit
    """

    n_players = 2

    create_folder_structure(repo, n_players)

    files = [
        os.path.join(repo.working_dir, "state", "game", "active_player"),
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "bank", "development_cards"),
        os.path.join(repo.working_dir, "state", "game", "discard_pile"),
        os.path.join(repo.working_dir, "state", "game", "settlement_points"),
        os.path.join(repo.working_dir, "state", "game", "road_points"),
        os.path.join(repo.working_dir, "state", "game", "bandit"),
        os.path.join(repo.working_dir, "state", "game", "turn_phase"),

        os.path.join(repo.working_dir, "state", "initialization", "active_player"),
        os.path.join(repo.working_dir, "state", "initialization", "init_phase")
    ]

    for i in range(n_players):
        files += [
            os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{i + 1}", "resource_cards"),
            os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{i + 1}", "bought_cards"),
            os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{i + 1}", "available_cards"),
            os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{i + 1}", "unveiled_cards"),
            os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{i + 1}"),
        ]

    for file_path in files:
        if not os.path.isfile(file_path):
            with open(file_path, "x") as file:
                val = ""
                if file_path.endswith("active_player"):
                    val = "1"
                elif file_path.endswith("init_phase"):
                    val = "phase_one"
                elif file_path.endswith(os.path.join(repo.working_dir, "bank","resource_cards")):
                    val = f"{_resource_card_pool}"
                elif file_path.endswith(os.path.join(repo.working_dir, "bank","development_cards")):
                    val = f"{_development_card_pool}"
                elif file_path.endswith("discard_pile"):
                    val = "(0,0,0)"
                elif file_path.endswith("settlement_points"):
                    for point in settlement_points:
                        val += f"{point}\n"
                elif file_path.endswith("road_points"):
                    for point in road_points:
                        val += f"{point}\n"
                elif file_path.endswith("bandit"):
                    val = "t112" # center tile
                elif file_path.endswith("turn_phase"):
                    val = "bot"
                file.write(val)


