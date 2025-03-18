import os
from random import randrange

import git
from gloabl_definitions import (
    _player_building_pool_str,
    _development_card_pool_str,
    _resource_card_pool_str,
    Settlement_point,
    Road_point,
    _player_colour,
    HexagonTile,
    _number_of_players,
    _player_colour_reversed
)
from repo_utils import get_repo_author_gitdir
from utils import (
    create_folder_structure,
    get_initial_active_player,
    get_all_available_settlement_points,
    get_all_settlement_points,
    get_all_road_points,
    get_all_available_road_points_for_settlement,
    update_active_player,
    update_settlement_point,
    update_road_point,
    get_settlement_point_index,
    get_road_point_index,
    update_initial_active_player,
    update_initial_phase,
    update_player_buildings,
    get_resources_from_hextile,
    update_player_hand,
    update_turn_phase,
    update_initial_active_player_rev,
    update_bank_resources,
    negate_int_arr,
)


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
    settlement_points: all initialized settlement points
    road_points: all initialized road points
    author_name: the name of the author
    email: the email of the author

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
                    val = "0"
                elif file_path.endswith("init_phase"):
                    val = "phase_one"
                elif file_path.__contains__("resource_cards") and file_path.__contains__("player_hands"):
                    val = "0,0,0,0,0"
                elif file_path.endswith(os.path.join("bank", "resource_cards")):
                    val = f"{_resource_card_pool_str}"
                elif file_path.endswith(os.path.join("bank","development_cards")):
                    val = f"{_development_card_pool_str}"
                elif file_path.endswith("bought_cards"):
                    val = "0,0,0"
                elif file_path.endswith("available_cards"):
                    val = "0,0,0"
                elif file_path.endswith("unveiled_cards"):
                    val = "0,0"
                elif file_path.__contains__(os.path.join("player_buildings", "player_")):
                    val = f"{_player_building_pool_str}"
                elif file_path.endswith("discard_pile"):
                    val = "0,0,0"
                elif file_path.endswith("settlement_points"):
                    for point in settlement_points:
                        val += f"{point}\n"
                elif file_path.endswith("road_points"):
                    for point in road_points:
                        val += f"{point}\n"
                elif file_path.endswith("bandit"):
                    val = "24" # center tile
                elif file_path.endswith("turn_phase"):
                    val = "bot"
                file.write(val)

    # add files to index
    for file_path in files:
        repo.index.add(file_path)
    repo.index.write_tree()

    author_name = get_repo_author_gitdir(repo.git_dir)
    author = git.Actor(author_name, f"{author_name}@git.com")
    comment_id = repo.index.commit(
        "Initial commit",
        [],
        True,
        author,
        author,
    )

    # change HEAD
    repo.git.update_ref(f"refs/heads/game_state", comment_id)

    return comment_id

def init_phase_one(repo: git.Repo, hexagons: [HexagonTile], parent: git.Commit) -> git.Commit:
    """
    Initialization phase one. Each player has to place a village and a road.

    Parameters
    ----------
    repo : current git repository

    Returns
    -------
    git.Commit
    """
    author_name = get_repo_author_gitdir(repo.git_dir)
    active_player = get_initial_active_player(repo)
    settlement_points = get_all_settlement_points(repo, hexagons)
    road_points = get_all_road_points(repo, hexagons)

    # compute all places we can place a settlement
    available_settlement_points = get_all_available_settlement_points(repo, settlement_points, active_player, hexagons)
    # choose a settlement
    pick = randrange(len(available_settlement_points))
    sp: Settlement_point = available_settlement_points[pick]
    sp.owner = _player_colour[active_player]
    sp.settlement_type = "Village"

    # compute all places we can place a road adjacent to a settlement
    available_road_points = get_all_available_road_points_for_settlement(repo, road_points, sp, active_player, hexagons)
    # choose a road
    pick = randrange(len(available_road_points))
    rp = available_road_points[pick]

    sp_id = get_settlement_point_index(sp, settlement_points)
    rp_id = get_road_point_index(rp, road_points)

    update_settlement_point(repo, sp_id, sp.owner, sp.settlement_type)
    update_road_point(repo, rp_id, _player_colour[active_player])

    # phase is over
    if active_player + 1 == _number_of_players:
        update_initial_phase(repo)
    else:
        update_initial_active_player(repo)
    update_player_buildings(repo, active_player, [-1,-1,0])

    files = [
        os.path.join(repo.working_dir, "state", "game", "settlement_points"),
        os.path.join(repo.working_dir, "state", "game", "road_points"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{active_player + 1}"),

        os.path.join(repo.working_dir, "state", "initialization", "active_player"),
        os.path.join(repo.working_dir, "state", "initialization", "init_phase")
    ]

    # add files to index
    for file_path in files:
        repo.index.add(file_path)
    repo.index.write_tree()

    author = git.Actor(author_name, f"{author_name}@git.com")
    commit_id = repo.index.commit(
        f"phase_one_player_{active_player}",
        [parent],
        True,
        author,
        author,
    )

    # change HEAD
    repo.git.update_ref(f"refs/heads/game_state", commit_id)

    return commit_id





def init_phase_two(repo: git.Repo, hexagons: [HexagonTile], parent: git.Commit) -> git.Commit:
    """
    Initialization phase one. Each player has to place a village and a road.

    Parameters
    ----------
    repo: current git repository
    hexagons: map hexagons
    parent: latest commit

    Returns
    -------
    git.Commit
    """
    author_name = get_repo_author_gitdir(repo.git_dir)
    active_player = get_initial_active_player(repo)
    settlement_points = get_all_settlement_points(repo, hexagons)
    road_points = get_all_road_points(repo, hexagons)

    # compute all places we can place a settlement
    available_settlement_points = get_all_available_settlement_points(repo, settlement_points, active_player, hexagons)
    # choose a settlement
    pick = randrange(len(available_settlement_points))
    sp = available_settlement_points[pick]
    sp.owner = _player_colour[active_player]
    sp.settlement_type = "Village"

    # compute all places we can place a road adjacent to a settlement
    available_road_points = get_all_available_road_points_for_settlement(repo, road_points, sp, active_player, hexagons)
    # choose a road
    pick = randrange(len(available_road_points))
    rp = available_road_points[pick]

    sp_id = get_settlement_point_index(sp, settlement_points)
    rp_id = get_road_point_index(rp, road_points)

    update_settlement_point(repo, sp_id, _player_colour[active_player], "Village")
    update_road_point(repo, rp_id, _player_colour[active_player])

    # get resources from second village
    resources = get_resources_from_hextile(sp.coords)
    update_player_hand(repo, "resource_cards", active_player, resources)
    update_bank_resources(repo, negate_int_arr(resources))

    # phase is over
    if active_player == 0:
        update_turn_phase(repo)

    update_initial_active_player_rev(repo)

    update_player_buildings(repo, active_player , [-1,-1,0])

    files = [
        os.path.join(repo.working_dir, "state", "game", "active_player"),
        os.path.join(repo.working_dir, "state", "game", "settlement_points"),
        os.path.join(repo.working_dir, "state", "game", "road_points"),
        os.path.join(repo.working_dir, "state", "game", "player_buildings", f"player_{active_player + 1}"),
        os.path.join(repo.working_dir, "state", "game", "player_hands", f"player_{active_player + 1}", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "bank", "resource_cards"),
        os.path.join(repo.working_dir, "state", "game", "turn_phase"),

        os.path.join(repo.working_dir, "state", "initialization", "active_player"),
        os.path.join(repo.working_dir, "state", "initialization", "init_phase")
    ]

    # add files to index
    for file_path in files:
        repo.index.add(file_path)
    repo.index.write_tree()

    author = git.Actor(author_name, f"{author_name}@git.com")
    commit_id = repo.index.commit(
        f"phase_two_player_{active_player}",
        [parent],
        True,
        author,
        author,
    )

    # change HEAD
    repo.git.update_ref(f"refs/heads/game_state", commit_id)

    return commit_id