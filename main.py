import os

import git
import pygame
from git import Repo, NoSuchPathError
from pygame import KEYUP, K_ESCAPE, K_RETURN
from pygame.event import EventType

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
    _screen_height, ROOT_DIR, _number_of_players, _player_colour_2_players, HexagonTile, _resource_card_pool,
    _development_card_pool, _player_building_pool,
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
    get_player_index, update_turn_phase, update_active_player, count_points, get_bandit, get_player_hand,
    get_bank_resources, get_bank_development_cards, get_discard_pile, get_all_settlements_of_player,
    get_all_roads_of_player, get_player_buildings,
)

def sim(with_ui=False):
    if with_ui:
        pygame.init()
        pygame.font.init()
        pygame.display.init()

        game = pygame.display.set_mode((_screen_width, _screen_height))
        game.fill((69, 139, 209))

        clock = pygame.time.Clock()
        hexagons = init_hexagons()

        render_static(game, hexagons)

    hexagons = init_hexagons()

    # check if there is already a game around
    try:
        repo = Repo(os.path.join(ROOT_DIR, "Catan"))
        init_state = get_initial_phase(repo)
    except NoSuchPathError:
        init_state = None

    # only initialize git and the points if no init state around
    if init_state is None:
        settlement_points = init_settlement_points(hexagons)
        road_points = init_road_points(hexagons)
        repo = create_git_dir()
        # initialize map and git folders
        player_nr = 0
        while player_nr < _number_of_players:
            # create a branch for each player
            player_name = _player_colour_2_players[player_nr]
            repo.git.checkout("-b", f"{player_name}")
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
            merge_repos(repo)
            if check_invariants(repo, hexagons):
                do_turn(repo, local_player, hexagons)
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
            merge_repos(repo)
            if check_invariants(repo, hexagons):
                do_turn(repo, local_player, hexagons)
            else:
                print(f"Illegal state {local_player}")
                terminated = True

    if with_ui:
        pygame.display.quit()


def switch_player(repo: git.Repo, local_player: int):
    # get next player
    next_player = (local_player + 1) % _number_of_players
    # change repo
    repo.git.checkout(f"{_player_colour_2_players[next_player]}")


def do_turn(repo: git.Repo, local_player: int, hexagons: [HexagonTile]):
    switch = False
    initial_phase = get_initial_phase(repo)
    turn_phase = get_turn_phase(repo)

    if turn_phase == "top":
        return
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

                points = count_points(repo, hexagons, local_player)
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
        switch_player(repo, local_player)

def merge_repos(repo: git.Repo):
    turn_phase = get_turn_phase(repo)
    local_player = get_player_index(repo.active_branch.name)

    # do not merge when a loss choice is being made
    if turn_phase == "dice_roll":
        if not repo.head.commit.message.__contains__("empty") and not repo.head.commit.message.__contains__(
                "loss"):
            # merge with other branches
            for i, player in enumerate(_player_colour_2_players):
                if i != local_player:
                    repo.git.merge(f"{player}", allow_unrelated_histories=True)
        else:
            repo.git.fetch()
    else:
        # merge with other branches
        for i, player in enumerate(_player_colour_2_players):
            if i != local_player:
                repo.git.merge(f"{player}", allow_unrelated_histories=True)

def check_invariants(repo: git.Repo, hexagons: [HexagonTile]) -> bool:
    res_cards = check_conservation_of_resource_cards(repo)
    dev_cards = check_conservation_of_development_cards(repo)
    buildings = check_conservation_of_player_buildings(repo, hexagons)

    return res_cards and dev_cards and buildings

def check_conservation_of_resource_cards(repo: git.Repo) -> bool:
    cards = get_bank_resources(repo)

    for player in range(_number_of_players):
        hand = get_player_hand(repo, "resource_cards", player)
        for i, resource in enumerate(hand):
            cards[i] += resource

    if cards == list(_resource_card_pool):
        return True
    else:
        return False

def check_conservation_of_development_cards(repo: git.Repo) -> bool:
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
                    cards[i] += bc[i] + ac[i] + uc[i-3]
                elif i == 4:
                    cards[i] += uc[i-3]

    if cards == list(_development_card_pool):
        return True
    else:
        return False

def check_conservation_of_player_buildings(repo: git.Repo, hexagons: [HexagonTile]) -> bool:
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
    return invariant

sim(True)