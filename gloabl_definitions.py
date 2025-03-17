from __future__ import annotations
import math
import os
from dataclasses import dataclass
from typing import Tuple, List
import pygame
from git import repo

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REMOTE_DIR = os.path.join(ROOT_DIR, "Remote")
TEST_DIR = os.path.join(ROOT_DIR, "Tests")


pygame.init()
pygame.font.init()
pygame.display.init()
_player_colour = ["Red", "Blue", "Green", "Orange"]
_player_colour_reversed = ["Orange", "Green", "Blue", "Red"]
_screen_width, _screen_height = pygame.display.get_desktop_sizes()[0]
_hexagon_radius = 100
_hex_num_width = 6
_hex_num_height = 7
_hexagon_height = 2 * _hexagon_radius
_hexagon_width = math.sqrt(3) * _hexagon_radius
_left_most_xy_coords = (((_screen_width - _hex_num_width * _hexagon_width) / 2) + _hex_num_width, (_screen_height - _hex_num_height * _hexagon_height) / 2)

_resource_card_type: Tuple[str, ...] = ("Lumber", "Brick", "Wool", "Grain", "Ore")
_progress_card_type: Tuple[str, ...] = ("Monopoly", "Year-of-Plenty", "Road-Building")
_development_card_type: Tuple[str, ...] = _progress_card_type + ("Knight", "Victory-Point")

_resource_card_pool: Tuple[int, ...] = (19, 19, 19, 19, 19)
_resource_card_pool_str: str = "19,19,19,19,19"
_development_card_pool: Tuple[int, ...] = (2, 2, 2, 14, 5)
_development_card_pool_str: str = "2,2,2,14,5"
_number_of_players = 2

@dataclass
class HexagonTile:
    """Hexagon class"""
    id: int
    radius: float
    position: Tuple[float, float]
    colour: Tuple[int, ...]
    number: int
    resource: str

    def __post_init__(self):
        self.vertices = self.compute_vertices()

    def __hash__(self):
        return hash(self.id)

    def compute_vertices(self) -> List[Tuple[float, float]]:
        """Returns a list of the hexagon's vertices as x, y tuples"""
        # pylint: disable=invalid-name
        x, y = self.position
        half_radius = self.radius / 2
        minimal_radius = self.minimal_radius
        return [
            (round(x, 1), round(y, 1)),
            (round(x - minimal_radius, 1), round(y + half_radius, 1)),
            (round(x - minimal_radius, 1), round(y + 3 * half_radius, 1)),
            (round(x, 1), round(y + 2 * self.radius, 1)),
            (round(x + minimal_radius, 1), round(y + 3 * half_radius, 1)),
            (round(x + minimal_radius, 1), round(y + half_radius, 1)),
        ]

    def compute_neighbours(self, hexagons: List[HexagonTile]) -> List[HexagonTile]:
        """Returns hexagons whose centres are two minimal radiuses away from self.centre"""
        # could cache results for performance
        return [hexagon for hexagon in hexagons if self.is_neighbour(hexagon)]

    def collide_with_point(self, point: Tuple[float, float]) -> bool:
        """Returns True if distance from centre to point is less than horizontal_length"""
        return math.dist(point, self.centre) < self.minimal_radius

    def is_neighbour(self, hexagon: HexagonTile) -> bool:
        """Returns True if hexagon centre is approximately
        2 minimal radiuses away from own centre
        """
        distance = math.dist(hexagon.centre, self.centre)
        return math.isclose(distance, 2 * self.minimal_radius, rel_tol=0.05)

    def render(self, screen) -> None:
        """Renders the hexagon on the screen"""
        pygame.draw.polygon(screen, self.colour, self.vertices)
        pygame.gfxdraw.aapolygon(screen, self.vertices, (255, 229, 153))
        if self.colour != (69, 139, 209) and self.colour != (255, 229, 153):
            number = pygame.image.load(f"Sprites/Map/number_{self.number}.png").convert_alpha()
            img_rect = number.get_rect(center=self.centre)
            screen.blit(number, img_rect.topleft)

    @property
    def centre(self) -> Tuple[float, float]:
        """Centre of the hexagon"""
        x, y = self.position  # pylint: disable=invalid-name
        return (x, y + self.radius)

    @property
    def minimal_radius(self) -> float:
        """Horizontal length of the hexagon"""
        # https://en.wikipedia.org/wiki/Hexagon#Parameters
        return self.radius * math.cos(math.radians(30))

class MapTile:
    arc_coords: [int]
    resource: str
    number: int

    def __init__(self, arr: int, row: int, col: int, resource: str, number: int):
        self.arc_coords = [arr, row, col]
        self.resource = resource
        self.number = number

_wharf_types: Tuple[str, ...] = ("3:1",) + _resource_card_type


Map: [MapTile] = [
    # Top Row Water
    MapTile(0, -1, -1, "Water", -1),
    MapTile(0, -1, 0, "Water", -1),
    MapTile(0, -1, 1, "Water", -1),
    MapTile(0, -1, 2, "Water", -1),
    MapTile(0, -1, 3, "Water", -1),
    MapTile(0, -1, 4, "Water", -1),
    MapTile(0, -1, 5, "Water", -1),

    # First Line of Island
    MapTile(1, 0, -1, "Water", -1),
    MapTile(1, 0, 0, "Water", -1),
    MapTile(1, 0, 1, "Ore", 10),
    MapTile(1, 0, 2, "Wool", 2),
    MapTile(1, 0, 3, "Lumber", 9),
    MapTile(1, 0, 4, "Water", -1),
    MapTile(1, 0, 5, "Water", -1),

    # Second Row of Island
    MapTile(0, 0, -1, "Water", -1),
    MapTile(0, 0, 0, "Grain", 12),
    MapTile(0, 0, 1, "Brick", 6),
    MapTile(0, 0, 2, "Wool", 4),
    MapTile(0, 0, 3, "Brick", 10),
    MapTile(0, 0, 4, "Water", -1),
    MapTile(0, 0, 5, "Water", -1),

    # Third Row of Island
    MapTile(1, 1, -1, "Water", -1),
    MapTile(1, 1, 0, "Grain", 9),
    MapTile(1, 1, 1, "Lumber", 11),
    MapTile(1, 1, 2, "Desert", -1),
    MapTile(1, 1, 3, "Lumber", 3),
    MapTile(1, 1, 4, "Ore", 8),
    MapTile(1, 1, 5, "Water", -1),

    # Fourth Row of Island
    MapTile(0, 1, -1, "Water", -1),
    MapTile(0, 1, 0, "Lumber", 8),
    MapTile(0, 1, 1, "Ore", 3),
    MapTile(0, 1, 2, "Grain", 4),
    MapTile(0, 1, 3, "Wool", 5),
    MapTile(0, 1, 4, "Water", -1),
    MapTile(0, 1, 5, "Water", -1),

    # Fifth Row of Island
    MapTile(1, 2, -1, "Water", -1),
    MapTile(1, 2, 0, "Water", -1),
    MapTile(1, 2, 1, "Brick", 5),
    MapTile(1, 2, 2, "Grain", 6),
    MapTile(1, 2, 3, "Wool", 11),
    MapTile(1, 2, 4, "Water", -1),
    MapTile(1, 2, 5, "Water", -1),

    # Water Row of Island
    MapTile(0, 2, -1, "Water", -1),
    MapTile(0, 2, 0, "Water", -1),
    MapTile(0, 2, 1, "Water", -1),
    MapTile(0, 2, 2, "Water", -1),
    MapTile(0, 2, 3, "Water", -1),
    MapTile(0, 2, 4, "Water", -1),
    MapTile(0, 2, 5, "Water", -1)
]

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
    Wharf(Map[1], Map[9], "3:1"),
    Wharf(Map[3], Map[10], "Grain"),
    Wharf(Map[12], Map[18], "Ore"),
    Wharf(Map[14], Map[15], "Lumber"),
    Wharf(Map[26], Map[27], "3:1"),
    Wharf(Map[28], Map[29], "Brick"),
    Wharf(Map[32], Map[40], "Wool"),
    Wharf(Map[37], Map[43], "3:1"),
    Wharf(Map[38], Map[45], "3:1"),
]

_settlement_type: Tuple[str, ...] = ("Village", "City")
_building_type: Tuple[str, ...] = ("Road",) + _settlement_type
_purchasable_item_type: Tuple[str, ...] = ("Development Card",) + _building_type

_player_building_pool: Tuple[int, ...] = (15, 5, 4)
_player_building_pool_str: str = "15,5,4"

class Settlement_point:
    coords: set[HexagonTile]
    owner: str
    settlement_type: str
    xy_coords: (float, float)

    def __init__(self, coords: set[HexagonTile], owner: str, settlement_type: str):
        self.coords = coords
        self.owner = owner
        if settlement_type in _settlement_type:
            self.settlement_type = settlement_type
        else:
            self.settlement_type = "bot"

        # vertex that is member of all three tiles is the correct point
        tiles = tuple(coords)
        tile_one = tiles[0]
        tile_two = tiles[1]
        tile_three = tiles[2]

        for vertex in tile_one.vertices:
            if vertex in tile_two.vertices and vertex in tile_three.vertices:
                self.xy_coords = vertex

    def render(self, screen) -> None:
        """Renders the hexagon on the screen"""

        if self.owner != "bot":
            if self.settlement_type == "Village":
                imp = pygame.image.load(f"Sprites/{self.owner}/Village.png").convert_alpha()
                img_rect = imp.get_rect(center=self.xy_coords)
                screen.blit(imp, img_rect.topleft)
            elif self.settlement_type == "City":
                imp = pygame.image.load(f"Sprites/{self.owner}/City.png").convert_alpha()
                img_rect = imp.get_rect(center=self.xy_coords)
                screen.blit(imp, img_rect.topleft)

    def coords_to_string(self):
        string = ""
        for coord in self.coords:
            string += f"{coord.id},"
        return string[:-1]

    def __str__(self):
        return f"{self.coords_to_string()},{self.owner},{self.settlement_type}"

class Road_point:
    coords: set[HexagonTile]
    owner: str
    xy_coords: (float, float)
    angle: int

    def __init__(self, coords: set[HexagonTile], owner: str):
        self.coords = coords
        self.owner = owner

        # two vertexes are member of both tiles
        tiles = tuple(coords)
        tile_one = tiles[0]
        tile_two = tiles[1]
        points = []

        for vertex in tile_one.vertices:
            if vertex in tile_two.vertices:
                points.append(vertex)

        self.xy_coords = (points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2


        x_1, y_1 = points[0]
        x_2, y_2 = points[1]
        deg = 0
        if x_1 < x_2 and y_1 < y_2 or x_1 > x_2 and y_1 > y_2:
            deg = -60
        elif x_1 < x_2 and y_1 > y_2 or x_1 > x_2 and y_1 < y_2:
            deg = 60
        elif x_1 == x_2:
            deg = 0
        elif y_1 == y_2:
            deg = 90

        self.angle = deg

    def coords_to_string(self):
        string = ""
        for coord in self.coords:
            string += f"{coord.id},"
        return string[:-1]

    def __str__(self):
        return f"{self.coords_to_string()},{self.owner}"

    def render(self, screen) -> None:
        """Renders the hexagon on the screen"""

        if self.owner != "bot":
            img = pygame.image.load(f"Sprites/{self.owner}/Road.png").convert_alpha()
            img_rot = pygame.transform.rotate(img, -self.angle)
            img_rect = img_rot.get_rect(center=self.xy_coords)
            screen.blit(img_rot, img_rect.topleft)

    def render_transparent(self, screen, player_colour: str):
        img = pygame.image.load(f"Sprites/{player_colour}/Road_t.png").convert_alpha()
        img_rot = pygame.transform.rotate(img, -self.angle)
        img_rect = img_rot.get_rect(center=self.xy_coords)
        screen.blit(img_rot, img_rect.topleft)