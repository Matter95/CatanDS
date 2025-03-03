from typing import Tuple

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
    coords:[int]
    resource: str
    number: int

    def __init__(self, arr: int, row: int, col: int, resource: str, number: int):
        self.coords = [arr, row, col]
        self.resource = resource
        self.number = number

@property
def coordinates(self):
    return self.coords

@property
def resource(self):
    return self.resource

@property
def number(self):
    return self.number

Map: [Tuple[str, MapTile]] = [
    # Top Row Water
    "t0m1m1", MapTile(0,-1,-1, "Bottom", -1),
    "t0m10", MapTile(0,-1,0, "Bottom", -1),
    "t0m11", MapTile(0, -1, 1, "Bottom", -1),
    "t0m12", MapTile(0, -1, 2, "Bottom", -1),
    "t0m13", MapTile(0, -1, 3, "Bottom", -1),
    "t0m14", MapTile(0, -1, 4, "Bottom", -1),
    "t0m15", MapTile(0, -1, 5, "Bottom", -1),

    # First Line of Island
    "t10m1", MapTile(1, 0, -1, "Bottom", -1),
    "t100", MapTile(1, 0, 0, "Bottom", -1),
    "t101", MapTile(1, 0, 1, "Ore", 10),
    "t102", MapTile(1, 0, 2, "Wool", 2),
    "t103", MapTile(1, 0, 3, "Lumber", 9),
    "t104", MapTile(1, 0, 4, "Bottom", -1),
    "t105", MapTile(1, 0, 5, "Bottom", -1),

    # Second Row of Island
    "t00m1", MapTile(0, 0, -1, "Bottom", -1),
    "t000", MapTile(0, 0, 0, "Grain", 12),
    "t001", MapTile(0, 0, 1, "Brick", 6),
    "t002", MapTile(0, 0, 2, "Wool", 4),
    "t003", MapTile(0, 0, 3, "Brick", 10),
    "t004", MapTile(0, 0, 4, "Bottom", -1),
    "t005", MapTile(0, 0, 5, "Bottom", -1),

    # Third Row of Island
    "t11m1", MapTile(1, 1, -1, "Bottom", -1),
    "t110", MapTile(1, 1, 0, "Grain", 9),
    "t111", MapTile(1, 1, 1, "Lumber", 11),
    "t112", MapTile(1, 1, 2, "Desert", -1),
    "t113", MapTile(1, 1, 3, "Lumber", 3),
    "t114", MapTile(1, 1, 4, "Ore", 8),
    "t115", MapTile(1, 1, 5, "Bottom", -1),

    # Fourth Row of Island
    "t01m1", MapTile(0, 1, -1, "Bottom", -1),
    "t010", MapTile(0, 1, 0, "Lumber", 8),
    "t011", MapTile(0, 1, 1, "Ore", 3),
    "t012", MapTile(0, 1, 2, "Grain", 4),
    "t013", MapTile(0, 1, 3, "Wool", 5),
    "t014", MapTile(0, 1, 4, "Bottom", -1),
    "t015", MapTile(0, 1, 5, "Bottom", -1),

    # Fifth Row of Island
    "t12m1", MapTile(1, 2, -1, "Bottom", -1),
    "t120", MapTile(1, 2, 0, "Bottom", -1),
    "t121", MapTile(1, 2, 1, "Brick", 5),
    "t122", MapTile(1, 2, 2, "Grain", 6),
    "t123", MapTile(1, 2, 3, "Wool", 11),
    "t124", MapTile(1, 2, 4, "Bottom", -1),
    "t125", MapTile(1, 2, 5, "Bottom", -1),

    # Bottom Row of Island
    "t02m1", MapTile(0, 2, -1, "Bottom", -1),
    "t020", MapTile(0, 2, 0, "Bottom", -1),
    "t021", MapTile(0, 2, 1, "Bottom", -1),
    "t022", MapTile(0, 2, 2, "Bottom", -1),
    "t023", MapTile(0, 2, 3, "Bottom", -1),
    "t024", MapTile(0, 2, 4, "Bottom", -1),
    "t025", MapTile(0, 2, 5, "Bottom", -1),
]

wharf_types: [str] = ["3:1"] + resource_card_type

def get_map_tile(name: str) -> MapTile:
    for tile in Map:
        if tile[0] == name:
            return tile[1]

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

settlement_type: str = ["Village", "City"]
building_type: str = ["Road"] + settlement_type
purchasable_item_type: str = building_type + ["Development Card"]

player_building_pool: dict[str, int] = {
    "Road": 15,
    "Village": 5,
    "City": 4,
}