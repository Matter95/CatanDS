from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List
from typing import Tuple
from gloabl_definitions import Map, MapTile, left_most_xy_coords, Map_alt, screen_width, screen_height
import pygame
import pygame.gfxdraw

"""
Taken and modified from
https://github.com/rbaltrusch/pygame_examples/blob/master/code/hexagonal_tiles/main.py
"""

@dataclass
class HexagonTile:
    """Hexagon class"""

    radius: float
    position: Tuple[float, float]
    colour: Tuple[int, ...]
    number: int

    def __post_init__(self):
        self.vertices = self.compute_vertices()

    def compute_vertices(self) -> List[Tuple[float, float]]:
        """Returns a list of the hexagon's vertices as x, y tuples"""
        # pylint: disable=invalid-name
        x, y = self.position
        half_radius = self.radius / 2
        minimal_radius = self.minimal_radius
        return [
            (x, y),
            (x - minimal_radius, y + half_radius),
            (x - minimal_radius, y + 3 * half_radius),
            (x, y + 2 * self.radius),
            (x + minimal_radius, y + 3 * half_radius),
            (x + minimal_radius, y + half_radius),
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
        #imp = pygame.image.load("Sprites/Map/TestHex.png").convert_alpha()

        #screen.blit(imp, self.centre)
        pygame.draw.polygon(screen, self.colour, self.vertices)
        pygame.gfxdraw.aapolygon(screen, self.vertices, (255, 229, 153))
        if self.colour != (69, 139, 209) and self.colour != (255, 229, 153):
            pygame.draw.circle(screen, (255, 229, 153), self.centre, radius=30)
        if self.number != -1:
            if self.number == 6 or self.number == 9:
                colour = (240, 0, 0)
            else:
                colour = (0, 0, 0)

            font = pygame.font.Font(None, 36)  # Use default font, size 36
            text_surface = font.render(f"{self.number}", True, colour)  # Render text
            text_rect = text_surface.get_rect(center=self.centre)  # Center the text inside hexagon
            screen.blit(text_surface, text_rect)
        if self.colour != (69, 139, 209) and self.colour != (255, 229, 153):
            for vertex in self.vertices:
                imp = pygame.image.load("Sprites/Map/Village_Red.png").convert_alpha()
                x,y = vertex
                size = 25
                screen.blit(imp, (x - size/2, y - size/2))

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


def create_hexagon(position, colour, number, radius=100) -> HexagonTile:
    """Creates a hexagon tile at the specified position"""
    return HexagonTile(radius=radius, colour=colour, position=position, number=number)


def render_map(screen):
    screen.fill((69, 139, 209))
    for tile in Map:
        if tile.resource == "Lumber":
            img = pygame.image.load("Sprites/Map/hex_lumber.png").convert_alpha()
        elif tile.resource == "Brick":
            img = pygame.image.load("Sprites/Map/hex_brick.png").convert_alpha()
        elif tile.resource == "Wool":
            img = pygame.image.load("Sprites/Map/hex_wool.png").convert_alpha()
        elif tile.resource == "Grain":
            img = pygame.image.load("Sprites/Map/hex_grain.png").convert_alpha()
        elif tile.resource == "Ore":
            img = pygame.image.load("Sprites/Map/hex_ore.png").convert_alpha()
        elif tile.resource == "Desert":
            img = pygame.image.load("Sprites/Map/hex_desert.png").convert_alpha()
        else:
            img = pygame.image.load("Sprites/Map/hex_water.png").convert_alpha()
        img_rect = img.get_rect(center=tile.xy_coords)
        screen.blit(img, img_rect.topleft)
    pygame.display.flip()


def init_hexagons(num_x=6, num_y=7) -> List[HexagonTile]:
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

    leftmost_hexagon = create_hexagon(left_most_xy_coords, colour_map(Map_alt[0]), Map_alt[0].number)
    hexagons = [leftmost_hexagon]
    j = 1

    for x in range(num_y):
        if x:
            # alternate between bottom left and bottom right vertices of hexagon above
            index = 2 if x % 2 == 1 else 4
            position = leftmost_hexagon.vertices[index]
            leftmost_hexagon = create_hexagon(position, colour_map(Map_alt[j]), Map_alt[j].number)
            hexagons.append(leftmost_hexagon)
            j += 1
        # place hexagons to the right of leftmost hexagon, with equal y-values.
        hexagon = leftmost_hexagon
        for i in range(num_x):
            x, y = hexagon.position  # type: ignore
            position = (x + hexagon.minimal_radius * 2, y)
            hexagon = create_hexagon(position, colour_map(Map_alt[j]), Map_alt[j].number)
            hexagons.append(hexagon)
            j += 1

    return hexagons


def render(screen, hexagons):
    """Renders hexagons on the screen"""
    screen.fill((0, 0, 0))
    for hexagon in hexagons:
        hexagon.render(screen)

    pygame.display.flip()


def main():
    """Main function"""

    info = pygame.display.Info()
    print(info)
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    render_map(screen)
    #hexagons = init_hexagons()
    terminated = False
    while not terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminated = True

        #render(screen, hexagons)

        clock.tick(50)
    pygame.display.quit()

main()