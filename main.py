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
    _screen_height, ROOT_DIR, _number_of_players, _player_colour_2_players,
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
    get_player_index, update_turn_phase, update_active_player, count_points,
)

def main():
    """Main function"""

    game = pygame.display.set_mode((_screen_width, _screen_height))
    game.fill((69, 139, 209))

    clock = pygame.time.Clock()
    hexagons = init_hexagons()

    render_static(game, hexagons)

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
        # pygame.time.Clock.tick(clock, 60)

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

        initial_phase = get_initial_phase(repo)
        turn_phase = get_turn_phase(repo)
        settlement_points = get_all_settlement_points(repo, hexagons)
        road_points = get_all_road_points(repo, hexagons)

        # render everything
        game.fill((69, 139, 209))
        render_static(game, hexagons)
        render_game_pieces(game, settlement_points, road_points)
        pygame.display.flip()

        if turn_phase == "top":
            terminated = True
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
            active_player = get_active_player(repo)
            # Dice Roll
            if turn_phase == "dice_roll":
                roll_dice(repo, hexagons)

            if active_player == local_player:

                if turn_phase == "trading":
                    trading(repo, hexagons)

                if turn_phase == "building":
                    building(repo, hexagons)

                    points = count_points(repo, hexagons, local_player)

                    if points >= 10:
                        update_turn_phase(repo, True)

        # get next player
        next_player = (local_player + 1) % _number_of_players
        # change repo
        repo.git.checkout(f"{_player_colour_2_players[next_player]}")

    pygame.display.quit()


main()