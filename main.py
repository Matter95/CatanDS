import os

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
from dice_roll import roll_dice
from gloabl_definitions import (
    _screen_width,
    _screen_height, ROOT_DIR,
)
from initializing import initialize_game_state, init_phase_one, init_phase_two
from utils import (
    get_initial_phase,
    get_turn_phase,
    get_all_settlement_points,
    get_all_road_points, create_git_dirs,
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
        repo = Repo(os.path.join(ROOT_DIR, "Catan_Alice"))
        latest_commit = repo.head.commit
        init_state = get_initial_phase(repo)
    except NoSuchPathError:
        init_state = None

    # only initialize git and the points if no init state around
    if init_state is None:
        settlement_points = init_settlement_points(hexagons)
        road_points = init_road_points(hexagons)
        repos = create_git_dirs()
        # initialize map and git folders
        for repo in repos:
            initialize_game_state(repo, settlement_points, road_points)
        repo = repos[0]
        latest_commit = repo.head.commit


    turn_phase = get_turn_phase(repo)

    terminated = False
    while not terminated:
        clock.tick(30)
        for event in pygame.event.get():
            initial_phase = get_initial_phase(repo)
            turn_phase = get_turn_phase(repo)
            settlement_points = get_all_settlement_points(repo, hexagons)
            road_points = get_all_road_points(repo, hexagons)
            render_game_pieces(game, settlement_points, road_points)

            # actions that are always possible
            if event.type == pygame.QUIT:
                terminated = True
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminated = True

            # we are in the initial phase
            if turn_phase == "bot":
                # Initial Phase One
                if initial_phase == "phase_one":
                    latest_commit = init_phase_one(repo, hexagons, latest_commit)
                # Initial Phase Two
                elif initial_phase == "phase_two":
                    latest_commit = init_phase_two(repo, hexagons, latest_commit)

            else:
                # Dice Roll
                #if turn_phase == "dice_roll":
                    #latest_commit = roll_dice(repo, hexagons, latest_commit)
                # Trading
                # No trade
                if event.type == KEYUP:
                    if event.key == K_RETURN:
                        pass
                # Choose Cards to Trade

                # Building
                # No building
                if event.type == KEYUP:
                    if event.key == K_RETURN:
                        pass




    pygame.display.quit()


main()