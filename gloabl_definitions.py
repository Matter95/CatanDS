import math
from typing import Tuple
import pygame


left_most_xy_coords = (800, 150)

pygame.init()
pygame.font.init()
pygame.display.init()
screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
middle_xy_coordinates: Tuple[float, float] = (screen_width / 2, screen_height / 2)
middle_arc_coordinates: Tuple[int, ...] = (1, 1, 2)

_hexagon_radius = 100
_hexagon_height = 2 * _hexagon_radius
_hexagon_width = math.sqrt(3) * _hexagon_radius

_resource_card_type: Tuple[str, ...] = ("Lumber", "Brick", "Wool", "Grain", "Ore")
_progress_card_type: Tuple[str, ...] = ("Monopoly", "Year-of-Plenty", "Road-Building")
_development_card_type: Tuple[str, ...] = _progress_card_type + ("Knight", "Victory-Point")

_resource_card_pool: dict[str, int] = {
    "Lumber": 19,
    "Brick": 19,
    "Wool": 19,
    "Grain": 19,
    "Ore": 19,
}
_development_card_pool: dict[str, int] = {
    "Monopoly": 2,
    "Year-of-Plenty": 2,
    "Road-Building": 2,
    "Knight": 14,
    "Victory-Point": 5,
}

class MapTile:
    designation: str
    arc_coords: [int]
    resource: str
    number: int
    xy_coords: [float, float]

    def __init__(self, designation: str, arr: int, row: int, col: int, resource: str, number: int):
        self.designation = designation
        self.arc_coords = [arr, row, col]
        self.resource = resource
        self.number = number

        x, y = middle_xy_coordinates
        # is leftmost hexagon
        if self.designation == "t112":
            self.xy_coords: [int, int] = (x, y)
        else:
            arr, row, col = self.arc_coords
            j = 1
            middle_arr, middle_row, middle_col = middle_arc_coordinates
            if middle_arr != arr:
                x += _hexagon_width / 2
                y += 0.75 * _hexagon_height

            if middle_row > row:
                row_diff = middle_row - row
                y -= row_diff * 1.5 * _hexagon_height
            elif middle_row < row:
                row_diff = row - middle_row
                y += row_diff * 1.5 * _hexagon_height

            if middle_col > col:
                col_diff = middle_col - col
                x -= col_diff * _hexagon_width
            elif middle_col < col:
                col_diff = col - middle_col
                x += col_diff * _hexagon_width

            self.xy_coords: [int, int] = (x, y)


Map: [MapTile] = [

    # Top Row Water
    MapTile("t0m10", 0, -1, 0, "Water", -1),
    MapTile("t0m11", 0, -1, 1, "Water", -1),
    MapTile("t0m12", 0, -1, 2, "Water", -1),
    MapTile("t0m13", 0, -1, 3, "Water", -1),

    # First Line of Island
    MapTile("t100", 1, 0, 0, "Water", -1),
    MapTile("t101", 1, 0, 1, "Ore", 10),
    MapTile("t102", 1, 0, 2, "Wool", 2),
    MapTile("t103", 1, 0, 3, "Lumber", 9),
    MapTile("t104", 1, 0, 4, "Water", -1),

    # Second Row of Island
    MapTile("t00m1", 0, 0, -1, "Water", -1),
    MapTile("t000", 0, 0, 0, "Grain", 12),
    MapTile("t001", 0, 0, 1, "Brick", 6),
    MapTile("t002", 0, 0, 2, "Wool", 4),
    MapTile("t003", 0, 0, 3, "Brick", 10),
    MapTile("t004", 0, 0, 4, "Water", -1),

    # Third Row of Island
    MapTile("t11m1", 1, 1, -1, "Water", -1),
    MapTile("t110", 1, 1, 0, "Grain", 9),
    MapTile("t111", 1, 1, 1, "Lumber", 11),
    MapTile("t112", 1, 1, 2, "Desert", -1),
    MapTile("t113", 1, 1, 3, "Lumber", 3),
    MapTile("t114", 1, 1, 4, "Ore", 8),
    MapTile("t115", 1, 1, 5, "Water", -1),

    # Fourth Row of Island
    MapTile("t01m1", 0, 1, -1, "Water", -1),
    MapTile("t010", 0, 1, 0, "Lumber", 8),
    MapTile("t011", 0, 1, 1, "Ore", 3),
    MapTile("t012", 0, 1, 2, "Grain", 4),
    MapTile("t013", 0, 1, 3, "Wool", 5),
    MapTile("t014", 0, 1, 4, "Water", -1),

    # Fifth Row of Island
    MapTile("t120", 1, 2, 0, "Water", -1),
    MapTile("t121", 1, 2, 1, "Brick", 5),
    MapTile("t122", 1, 2, 2, "Grain", 6),
    MapTile("t123", 1, 2, 3, "Wool", 11),
    MapTile("t124", 1, 2, 4, "Water", -1),

    # Bottom Row of Island
    MapTile("t020", 0, 2, 0, "Water", -1),
    MapTile("t021", 0, 2, 1, "Water", -1),
    MapTile("t022", 0, 2, 2, "Water", -1),
    MapTile("t023", 0, 2, 3, "Water", -1),
]

_wharf_types: Tuple[str, ...] = ("3:1",) + _resource_card_type

def get_map_tile(c: str) -> MapTile | None:
    for tile in Map:
        if tile.designation == c:
            return tile
    return None

class Wharf:
    coords:[MapTile]
    wharf_type: str

    def __init__(self, t1: MapTile, t2: MapTile, wharf_type: str):
        self.coords = [t1, t2]
        self.resource = wharf_type

Wharfs: [Wharf] = [
    Wharf(get_map_tile("t0m10"), get_map_tile("t101"), "3:1"),
    Wharf(get_map_tile("t0m12"), get_map_tile("t102"), "Grain"),
    Wharf(get_map_tile("t104"), get_map_tile("t003"), "Ore"),
    Wharf(get_map_tile("t00m1"), get_map_tile("t000"), "Lumber"),
    Wharf(get_map_tile("t114"), get_map_tile("t115"), "3:1"),
    Wharf(get_map_tile("t01m1"), get_map_tile("t010"), "Brick"),
    Wharf(get_map_tile("t013"), get_map_tile("t124"), "Wool"),
    Wharf(get_map_tile("t121"), get_map_tile("t020"), "3:1"),
    Wharf(get_map_tile("t122"), get_map_tile("t022"), "3:1"),
]

_settlement_type: Tuple[str, ...] = ("Village", "City")
_building_type: Tuple[str, ...] = ("Road",) + _settlement_type
_purchasable_item_type: Tuple[str, ...] = ("Development Card",) + _building_type

player_building_pool: dict[str, int] = {
    "Road": 15,
    "Village": 5,
    "City": 4,
}

class Settlement_point:
    designation: str
    coords: Tuple[MapTile, ...]
    xy_coords: Tuple[float, float]
    owner: str
    settlement_type: str

    def __init__(self, designation: str, coords: Tuple[MapTile, ...], owner: str, settlement_type: str):
        self.designation = designation
        self.coords = coords
        self.owner = owner
        if settlement_type in _settlement_type:
            self.settlement_type = settlement_type
        else:
            self.settlement_type = "bot"

    def __str__(self):
        return f"{self.designation}, {self.coords}, {self.xy_coords} {self.owner}, {self.settlement_type}"

class Road_point:
    designation: str
    coords: Tuple[MapTile, MapTile]
    xy_coords: Tuple[float, float]
    owner: str

    def __init__(self, designation: str, coords: Tuple[MapTile, MapTile], owner: str):
        self.designation = designation
        self.coords = coords
        self.owner = owner

    def __str__(self):
        return f"{self.designation}, {self.coords}, {self.xy_coords} {self.owner}"
