import os
from math import ceil

import git
import pygame
from git import Repo, NoSuchPathError
from pygame import KEYUP, K_ESCAPE

from UI import (
    init_hexagons,
    render_static,
    init_settlement_points,
    init_road_points,
    render_game_pieces
)
from building import building
from dice_roll import roll_dice
from gloabl_definitions import (
    _screen_width,
    _screen_height, ROOT_DIR, _number_of_players, HexagonTile, _resource_card_pool,
    _development_card_pool, _player_building_pool, get_player_colour,
)
from initializing import (
    initialize_game_state,
    init_phase_one,
    init_phase_two
)
from trading import trading
from utils import (
    get_initial_phase,
    get_turn_phase,
    get_all_settlement_points,
    get_all_road_points,
    create_git_dir,
    get_active_player,
    get_initial_active_player,
    get_player_index,
    update_turn_phase,
    count_points,
    get_bandit,
    get_player_hand,
    get_bank_resources,
    get_bank_development_cards,
    get_discard_pile,
    get_all_settlements_of_player,
    get_all_roads_of_player,
    get_player_buildings, get_longest_road, get_mightiest_army,
)


def sim(repo_folder_nr=-1, with_ui=False):
    """
    Simulates a game of Catan with or without UI. Writes a repo into Catan_{repo_folder_nr}

    Parameters
    ----------
    repo_folder_nr : simulation number
    with_ui : activates pygame UI
    """
    if with_ui:
        pygame.init()
        pygame.font.init()
        pygame.display.init()

        game = pygame.display.set_mode((_screen_width, _screen_height))
        game.fill((69, 139, 209))

        hexagons = init_hexagons()

        render_static(game, hexagons)

    hexagons = init_hexagons()
    longest_road = -1
    mightiest_army = -1
    # check if there is already a game around
    try:
        repo = Repo(os.path.join(ROOT_DIR, f"Catan_{repo_folder_nr}"))
        init_state = get_initial_phase(repo)
    except NoSuchPathError:
        init_state = None

    # only initialize git and the points if no init state around
    if init_state is None:
        settlement_points = init_settlement_points(hexagons)
        road_points = init_road_points(hexagons)
        repo = create_git_dir(f"Catan_{repo_folder_nr}")
        # initialize map and git folders
        player_nr = 0
        while player_nr < _number_of_players:
            # create a branch for each player
            player_name = get_player_colour(_number_of_players)[player_nr]
            repo.git.checkout("-b", f"{player_name}_{repo_folder_nr}")
            if player_nr == 0:
                initialize_game_state(repo, settlement_points, road_points, player_name)
            else:
                repo.index.write_tree()

                author = git.Actor(player_name, f"{player_name}@git.com")
                repo.index.commit(
                    f"Initial commit player_{player_name}",
                    [],
                    True,
                    author,
                    author,
                )

            player_nr += 1

    terminated = False
    while not terminated:
        if with_ui:
            for event in pygame.event.get():
                # actions that are always possible
                if event.type == pygame.QUIT:
                    terminated = True
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        terminated = True

            local_player = get_player_index(repo.active_branch.name)
            merge_repos(repo, repo_folder_nr)
            if check_invariants(repo, hexagons):
                longest_road, mightiest_army, finished = do_turn(repo, local_player, hexagons, repo_folder_nr, longest_road, mightiest_army)
            else:
                print(f"Illegal state {local_player}")
                terminated = True
            settlement_points = get_all_settlement_points(repo, hexagons)
            road_points = get_all_road_points(repo, hexagons)
            bandit = get_bandit(repo, hexagons)

            # render everything
            game.fill((69, 139, 209))
            render_static(game, hexagons)
            render_game_pieces(game, settlement_points, road_points, bandit)
            pygame.display.flip()
        else:
            local_player = get_player_index(repo.active_branch.name)
            merge_repos(repo, repo_folder_nr)
            if check_invariants(repo, hexagons):
                longest_road, mightiest_army, finished = do_turn(repo, local_player, hexagons, repo_folder_nr, longest_road, mightiest_army)
                if finished:
                    terminated = True
            else:
                print(f"Illegal state {local_player}")
                terminated = True
    if with_ui:
        pygame.display.quit()


def switch_player(repo: git.Repo, local_player: int, repo_folder_nr: int):
    """
    Switches active player to the next player in line and switches to said players git branch.

    Parameters
    ----------
    repo: current player
    local_player: player branch we are currently on
    repo_folder_nr: simulation number
    """
    # get next player
    next_player = (local_player + 1) % _number_of_players
    # change repo
    repo.git.checkout(f"{get_player_colour(_number_of_players)[next_player]}_{repo_folder_nr}")


def do_turn(repo: git.Repo, local_player: int, hexagons: [HexagonTile], repo_folder_nr: int, longest_road: int, mightiest_army: int):
    """
    Logic that forces a player to take the action of the given turn phase and only allows the active player
    to change the state of the game.

    Parameters
    ----------
    repo: current player
    local_player: player branch we are currently on
    hexagons: map tiles
    repo_folder_nr: simulation number
    """
    switch = False
    initial_phase = get_initial_phase(repo)
    turn_phase = get_turn_phase(repo)

    if turn_phase == "top":
        return -1, -1, True
    # we are in the initial phase
    elif turn_phase == "bot":
        active_player = get_initial_active_player(repo)

        if active_player == local_player:
            # Initial Phase One
            if initial_phase == "phase_one":
                init_phase_one(repo, hexagons)
            # Initial Phase Two
            elif initial_phase == "phase_two":
                init_phase_two(repo, hexagons)
        else:
            switch = True
    else:
        active_player = get_active_player(repo)
        # Dice Roll
        if turn_phase == "dice_roll":
            roll_dice(repo, hexagons)
            switch = True
        if active_player == local_player:

            if turn_phase == "trading":
                trading(repo, hexagons)

            if turn_phase == "building":
                building(repo, hexagons)

                temp_road = get_longest_road(repo, local_player, hexagons)
                if temp_road != -1:
                    longest_road = temp_road
                else:
                    longest_road = -1
                temp_army = get_mightiest_army(repo, local_player)
                if temp_army != -1:
                    mightiest_army = temp_army
                else:
                    mightiest_army = -1
                points = count_points(repo, hexagons, local_player, longest_road, mightiest_army)
                if points >= 10:
                    update_turn_phase(repo, True)
                    repo.index.add(os.path.join(os.path.join(repo.working_dir, "state", "game", "turn_phase")))

                    author_name = repo.active_branch.name
                    author = git.Actor(author_name, f"{author_name}@git.com")
                    repo.index.commit(
                        f"victory_player{local_player + 1}",
                        [repo.head.commit],
                        True,
                        author,
                        author,
                    )
                    switch = True
        else:
            switch = True

    if switch:
        switch_player(repo, local_player, repo_folder_nr)
    return mightiest_army, longest_road, False


def merge_repos(repo: git.Repo, repo_folder_nr: int):
    """
    merges all branches of the different players

    Parameters
    ----------
    repo : current repository
    repo_folder_nr : current simulation number
    """
    turn_phase = get_turn_phase(repo)
    local_player = get_player_index(repo.active_branch.name)

    # do not merge when a loss choice is being made (conflict is resolved elsewhere)
    if turn_phase == "dice_roll":
        if not repo.head.commit.message.__contains__("empty") and not repo.head.commit.message.__contains__(
                "loss"):
            # merge with other branches
            for i, player in enumerate(get_player_colour(_number_of_players)):
                if i != local_player:
                    repo.git.merge(f"{player}_{repo_folder_nr}", allow_unrelated_histories=True)

        else:
            repo.git.fetch()
    else:
        # merge with other branches
        for i, player in enumerate(get_player_colour(_number_of_players)):
            if i != local_player:
                repo.git.merge(f"{player}_{repo_folder_nr}", allow_unrelated_histories=True)


def check_invariants(repo: git.Repo, hexagons: [HexagonTile]) -> bool:
    """
    Checks all invariants.

    Parameters
    ----------
    repo : current repository
    hexagons : map tiles

    Returns
    -------
    If invariants hold, returns true, else returns false
    """
    res_cards = check_conservation_of_resource_cards(repo)
    dev_cards = check_conservation_of_development_cards(repo)
    buildings = check_conservation_of_player_buildings(repo, hexagons)

    return res_cards and dev_cards and buildings


def check_conservation_of_resource_cards(repo: git.Repo) -> bool:
    """
    Invariant for resource cards. Checks if cards of all the players hand and bank are equal to the
    whole resource card pool.

    Parameters
    ----------
    repo : current repository

    Returns
    -------
    If invariant holds, returns true, else returns false
    """
    cards = get_bank_resources(repo)

    for player in range(_number_of_players):
        hand = get_player_hand(repo, "resource_cards", player)
        for i, resource in enumerate(hand):
            cards[i] += resource

    if cards == list(_resource_card_pool):
        return True
    else:
        print(f"illegal state res cards: current: {cards}; expected: {_resource_card_pool}")
        return False


def check_conservation_of_development_cards(repo: git.Repo) -> bool:
    """
    Invariant for development cards. Checks if cards in the players' hands, bank and discard pile are equal to the
    whole development card pool.

    Parameters
    ----------
    repo : current repository

    Returns
    -------
    If invariant holds, returns true, else returns false
    """
    cards = get_bank_development_cards(repo)
    # sum the cards of all players
    discard_pile = get_discard_pile(repo)

    for i, resource in enumerate(discard_pile):
        cards[i] += resource

    for player in range(_number_of_players):
        bc = get_player_hand(repo, "bought_cards", player)
        ac = get_player_hand(repo, "available_cards", player)
        uc = get_player_hand(repo, "unveiled_cards", player)
        for i, resource in enumerate(cards):
            if 0 <= i < 3:
                cards[i] += bc[i] + ac[i]
            elif i >= 3:
                if i == 3:
                    cards[i] += bc[i] + ac[i] + uc[i - 3]
                elif i == 4:
                    cards[i] += uc[i - 3]

    if cards == list(_development_card_pool):
        return True
    else:
        print(f"illegal state dev cards: current: {cards}; expected: {_development_card_pool}")
        return False


def check_conservation_of_player_buildings(repo: git.Repo, hexagons: [HexagonTile]) -> bool:
    """
    Invariant for player buildings. Checks if pieces on the board and in the
    players building pool are equivalent to the starting amount of buildings.

    Parameters
    ----------
    repo : current repository
    hexagons : map tiles

    Returns
    -------
    If invariant holds, returns true, else returns false
    """
    invariant = True

    sps = get_all_settlement_points(repo, hexagons)
    rps = get_all_road_points(repo, hexagons)
    for player in range(_number_of_players):
        buildings = get_player_buildings(repo, player)
        settlements = get_all_settlements_of_player(sps, player)
        roads = get_all_roads_of_player(rps, player)

        buildings[0] += len(roads)
        for sp in settlements:
            if sp.type in "Village":
                buildings[1] += 1
            elif sp.type in "City":
                buildings[2] += 1

        if buildings != list(_player_building_pool):
            invariant = False
            print(f"illegal state buildings: current: {buildings}; expected: {_player_building_pool}")
    return invariant


def get_stats(repo_folder):
    """
    Gather statistics from the game runs and writes it into the stats file

    Parameters
    ----------
    repo_folder : name of the repo to gather stats from

    -------
    """
    repo = Repo(os.path.join(ROOT_DIR, repo_folder))
    total_bytes = 0
    nr_commits = 0
    nr_rounds = 0
    # Iterate through all commits
    for commit in repo.iter_commits():
        if commit.message.__contains__("finish_building"):
            nr_rounds += 1
        nr_commits += 1
        if commit.parents:  # Ensure commit has a parent
            diff = commit.diff(commit.parents[0], create_patch=True)
            for change in diff:
                if change.diff:
                    total_bytes += len(change.diff)
    if not os.path.isfile(os.path.join(ROOT_DIR, "stats")):
        with open(os.path.join(ROOT_DIR, "stats"), "x") as f:
            pass
    with open(os.path.join(ROOT_DIR, "stats"), "a") as f:
        f.write(f"{total_bytes / 1000};{nr_commits};{ceil(nr_rounds / _number_of_players)}\n")


def simulate(number_of_sims: int):
    for i in range(number_of_sims):
        sim(i, False)

def take_statistics(number_of_sims: int):
    for i in range(number_of_sims):
        get_stats(f"Catan_{i}")


simulate(1)
