import os
from typing import List
from typing import Tuple

import git

from gloabl_definitions import (
    Map,
    MapTile,
    _left_most_xy_coords,
    _hexagon_radius,
    _hex_num_width,
    _hex_num_height, HexagonTile, Road_point, Settlement_point, ROOT_DIR, REMOTE_DIR, _player_colour_2_players
)
import pygame
import pygame.gfxdraw

"""
Taken and modified from
https://github.com/rbaltrusch/pygame_examples/blob/master/code/hexagonal_tiles/main.py
"""

def create_hexagon(id, position, colour, number, resource, radius=_hexagon_radius) -> HexagonTile:
    """Creates a hexagon tile at the specified position"""
    return HexagonTile(id=id, radius=radius, colour=colour, position=position, number=number, resource=resource)

def init_hexagons(num_x=_hex_num_width, num_y=_hex_num_height) -> List[HexagonTile]:
    """Creates a hexaogonal tile map of size num_x * num_y"""
    # pylint: disable=invalid-name

    def colour_map(tile: MapTile) -> Tuple[int, ...]:
        if tile.resource == "Lumber":
            return (37, 162, 37)
        elif tile.resource == "Brick":
            return (214, 114, 19)
        elif tile.resource == "Wool":
            return (153, 219, 87)
        elif tile.resource == "Grain":
            return (242, 211, 54)
        elif tile.resource == "Ore":
            return (153, 153, 153)
        elif tile.resource == "Desert":
            return (255, 229, 153)
        else:
            return (69, 139, 209)

    leftmost_hexagon = create_hexagon(0, _left_most_xy_coords, colour_map(Map[0]), Map[0].number, Map[0].resource)
    hexagons = [leftmost_hexagon]
    j = 1

    for x in range(num_y):
        if x:
            # alternate between bottom left and bottom right vertices of hexagon above
            index = 2 if x % 2 == 1 else 4
            position = leftmost_hexagon.vertices[index]
            leftmost_hexagon = create_hexagon(j, position, colour_map(Map[j]), Map[j].number, Map[j].resource)
            hexagons.append(leftmost_hexagon)
            j += 1
        # place hexagons to the right of leftmost hexagon, with equal y-values.
        hexagon = leftmost_hexagon
        for i in range(num_x):
            x, y = hexagon.position  # type: ignore
            position = (x + hexagon.minimal_radius * 2, y)
            hexagon = create_hexagon(j, position, colour_map(Map[j]), Map[j].number, Map[j].resource)
            hexagons.append(hexagon)
            j += 1

    return hexagons

def init_settlement_points(hexagons: [HexagonTile]) -> List[Settlement_point]:
    """Creates a list of all settlement points."""
    settlement_points = []
    index = 0
    for tile_one in hexagons:
        for tile_two in hexagons:
            if tile_two == tile_one:
                continue
            for tile_three in hexagons:
                if tile_three == tile_two:
                    continue
                # tiles need to be adjacent
                if (
                    tile_one.is_neighbour(tile_two) and tile_one.is_neighbour(tile_three)
                    and tile_two.is_neighbour(tile_three)
                ):
                   # at least one tile should not be water
                    if tile_one.resource != "Water" or tile_two.resource != "Water" or tile_three.resource != "Water":
                        exists = False
                        for point in settlement_points:
                            if tile_one in point.coords and tile_two in point.coords and tile_three in point.coords:
                                exists = True
                        if not exists:
                            settlement_points.append(Settlement_point(index, {tile_one, tile_two, tile_three}, "bot", "bot"))
                            index += 1
    return settlement_points

def init_road_points(hexagons: [HexagonTile]) -> List[Road_point]:
    """Creates a list of all settlement points."""
    road_points = []
    index = 0

    for tile_one in hexagons:
        for tile_two in hexagons:
            if tile_two == tile_one:
                continue
            # tiles need to be adjacent
            if tile_one.is_neighbour(tile_two):
               # at least one tile should not be water
                if tile_one.resource != "Water" or tile_two.resource != "Water":
                    exists = False
                    for point in road_points:
                        if tile_one in point.coords and tile_two in point.coords:
                            exists = True
                    if not exists:
                        road_points.append(Road_point(index, {tile_one, tile_two}, "bot"))
                        index += 1
    return road_points

def render_static(screen, hexagons):
    """Renders hexagons on the screen"""
    for hexagon in hexagons:
        hexagon.render(screen)

def render_transparent(screen, settlement_points: [Settlement_point], road_points: [Road_point], player_nr):
    for settlement_point in settlement_points:
        settlement_point.render(screen)
    for road_point in road_points:
        road_point.render_transparent(screen, _player_colour_2_players[player_nr])
    pygame.display.flip()

def render_game_pieces(screen, settlement_points: [Settlement_point], road_points: [Road_point]):
    """Renders hexagons on the screen"""
    for point in settlement_points:
        point.render(screen)
    for point in road_points:
        point.render(screen)

def render_player_cards(screen, player_hand):
    pass