from __future__ import annotations
from hexalattice.hexalattice import *
import random

import math
from dataclasses import dataclass
from typing import List
from typing import Tuple
from gloabl_definitions import Map, MapTile
import pygame

def print_map():
    hex_centers, _ = create_hex_grid(
        nx=7,
        ny=7,
        do_plot=False
    )

    x_hex_coords = hex_centers[:, 0]
    y_hex_coords = hex_centers[:, 1]

    plot_single_lattice_custom_colors(x_hex_coords, y_hex_coords,
                                          face_color="beige",
                                          edge_color="beige",
                                          min_diam=1,
                                          plotting_gap=0,
                                          rotate_deg=0)
    plt.show()


"""
Created on Sun Jan 23 14:07:18 2022

@author: richa
"""
@dataclass
class HexagonTile:
    """Hexagon class"""

    radius: float
    position: Tuple[float, float]
    colour: Tuple[int, ...]

    def __post_init__(self):
        self.vertices = self.compute_vertices()
        self.highlight_tick = 0

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
        pygame.draw.polygon(screen, self.colour, self.vertices)
        pygame.draw.polygon(screen, (255, 229, 153), self.vertices, 4)
        if self.colour != [69, 139, 209] and self.colour != [255, 229, 153]:
            pygame.draw.circle(screen, (255, 229, 153), self.centre, radius=30, width=4)


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



def create_hexagon(position, colour, radius=100) -> HexagonTile:
    """Creates a hexagon tile at the specified position"""
    return HexagonTile(radius=radius, colour=colour, position=position)

def get_random_colour(min_=150, max_=255) -> Tuple[int, ...]:
    """Returns a random RGB colour with each component between min_ and max_"""
    return tuple(random.choices(list(range(min_, max_)), k=3))

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

    leftmost_hexagon = create_hexagon(position=(60, 10), colour=colour_map(Map[0][1]))
    hexagons = [leftmost_hexagon]
    j = 1

    for x in range(num_y):
        if x:
            # alternate between bottom left and bottom right vertices of hexagon above
            index = 2 if x % 2 == 1 else 4
            position = leftmost_hexagon.vertices[index]
            leftmost_hexagon = create_hexagon(position, colour=colour_map(Map[j][1]))
            hexagons.append(leftmost_hexagon)
            j += 1
        # place hexagons to the right of leftmost hexagon, with equal y-values.
        hexagon = leftmost_hexagon
        for i in range(num_x):
            x, y = hexagon.position  # type: ignore
            position = (x + hexagon.minimal_radius * 2, y)
            hexagon = create_hexagon(position, colour=colour_map(Map[j][1]))
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
    pygame.init()
    screen = pygame.display.set_mode((1200, 1200))
    clock = pygame.time.Clock()
    hexagons = init_hexagons()
    terminated = False
    while not terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminated = True

        render(screen, hexagons)
        clock.tick(50)
    pygame.display.quit()

if __name__ == "__main__":
    main()