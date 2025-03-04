import math
from typing import Tuple

left_most_xy_coords = (800, 150)
left_most_arc_coords = (0, -1, -1)

hexagon_radius = 100



resource_card_type: [str] = ["Lumber", "Brick", "Wool", "Grain", "Ore"]
progress_card_type: [str] = ["Monopoly", "Year-of-Plenty", "Road-Building"]
development_card_type: [str] = progress_card_type + ["Knight", "Victory-Point"]

resource_card_pool: dict[str, int] = {
    "Lumber": 19,
    "Brick": 19,
    "Wool": 19,
    "Grain": 19,
    "Ore": 19,
}
development_card_pool: dict[str, int] = {
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
    xy_coords: [int, int]

    def __init__(self, designation: str, arr: int, row: int, col: int, resource: str, number: int):
        self.designation = designation
        self.arc_coords = [arr, row, col]
        self.resource = resource
        self.number = number

        x = 800
        y = 150
        # is leftmost hexagon
        if self.designation == "t0m1m1":
            self.xy_coords: [int, int] = (x, y)
        else:
            arr, row, col = self.arc_coords
            j = 1
            spacing_width = math.sqrt(3) * hexagon_radius
            spacing_height = 2 / 3 * hexagon_radius

            row_diff = abs(-1 - row)
            col_diff = abs(-1 - col)

            if arr == 0:
                x -= spacing_width / 2

            x += col_diff * spacing_width
            y += row_diff * spacing_height
            self.xy_coords: [int, int] = (x, y)


Map: [Tuple[MapTile]] = [
    # Top Row Water
    MapTile("t0m1m1", 0, -1, -1, "Bottom", -1),
    MapTile("t0m10", 0,-1,0, "Bottom", -1),
    MapTile("t0m11", 0, -1, 1, "Bottom", -1),
    MapTile("t0m12", 0, -1, 2, "Bottom", -1),
    MapTile("t0m13", 0, -1, 3, "Bottom", -1),
    MapTile("t0m14", 0, -1, 4, "Bottom", -1),
    MapTile("t0m15", 0, -1, 5, "Bottom", -1),

    # First Line of Island
    MapTile("t10m1", 1, 0, -1, "Bottom", -1),
    MapTile("t100", 1, 0, 0, "Bottom", -1),
    MapTile("t101", 1, 0, 1, "Ore", 10),
    MapTile("t102", 1, 0, 2, "Wool", 2),
    MapTile("t103", 1, 0, 3, "Lumber", 9),
    MapTile("t104", 1, 0, 4, "Bottom", -1),
    MapTile("t105", 1, 0, 5, "Bottom", -1),

    # Second Row of Island
    MapTile("t00m1", 0, 0, -1, "Bottom", -1),
    MapTile("t000", 0, 0, 0, "Grain", 12),
    MapTile("t001", 0, 0, 1, "Brick", 6),
    MapTile("t002", 0, 0, 2, "Wool", 4),
    MapTile("t003", 0, 0, 3, "Brick", 10),
    MapTile("t004", 0, 0, 4, "Bottom", -1),
    MapTile("t005", 0, 0, 5, "Bottom", -1),

    # Third Row of Island
    MapTile("t11m1", 1, 1, -1, "Bottom", -1),
    MapTile("t110", 1, 1, 0, "Grain", 9),
    MapTile("t111", 1, 1, 1, "Lumber", 11),
    MapTile("t112", 1, 1, 2, "Desert", -1),
    MapTile("t113", 1, 1, 3, "Lumber", 3),
    MapTile("t114", 1, 1, 4, "Ore", 8),
    MapTile("t115", 1, 1, 5, "Bottom", -1),

    # Fourth Row of Island
    MapTile("t01m1", 0, 1, -1, "Bottom", -1),
    MapTile("t010", 0, 1, 0, "Lumber", 8),
    MapTile("t011", 0, 1, 1, "Ore", 3),
    MapTile("t012", 0, 1, 2, "Grain", 4),
    MapTile("t013", 0, 1, 3, "Wool", 5),
    MapTile("t014", 0, 1, 4, "Bottom", -1),
    MapTile("t015", 0, 1, 5, "Bottom", -1),

    # Fifth Row of Island
    MapTile("t12m1", 1, 2, -1, "Bottom", -1),
    MapTile("t120", 1, 2, 0, "Bottom", -1),
    MapTile("t121", 1, 2, 1, "Brick", 5),
    MapTile("t122", 1, 2, 2, "Grain", 6),
    MapTile("t123", 1, 2, 3, "Wool", 11),
    MapTile("t124", 1, 2, 4, "Bottom", -1),
    MapTile("t125", 1, 2, 5, "Bottom", -1),

    # Bottom Row of Island
    MapTile("t02m1", 0, 2, -1, "Bottom", -1),
    MapTile("t020", 0, 2, 0, "Bottom", -1),
    MapTile("t021", 0, 2, 1, "Bottom", -1),
    MapTile("t022", 0, 2, 2, "Bottom", -1),
    MapTile("t023", 0, 2, 3, "Bottom", -1),
    MapTile("t024", 0, 2, 4, "Bottom", -1),
    MapTile("t025", 0, 2, 5, "Bottom", -1)
]

wharf_types: [str] = ["3:1"] + resource_card_type

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

settlement_type: [str] = ["Village", "City"]
building_type: [str] = ["Road"] + settlement_type
purchasable_item_type: [str] = building_type + ["Development Card"]

player_building_pool: dict[str, int] = {
    "Road": 15,
    "Village": 5,
    "City": 4,
}