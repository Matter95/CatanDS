import os
from unittest import TestCase

from git import Repo, NoSuchPathError

from Tests.test_repo_utils import delete_repo
from UI import init_settlement_points, init_road_points, init_hexagons
from gloabl_definitions import TEST_DIR
from initializing import initialize_game_state
from utils import (
    get_initial_phase,
    update_road_point,
    create_git_dir_test, has_longest_road
)


class TestInputOutput(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.hexagons = TestInputOutput.hexagons
        self.settlement_points = TestInputOutput.settlement_points
        self.road_points = TestInputOutput.road_points
        self.repo = TestInputOutput.repo

    @classmethod
    def setUpClass(cls):
        """ get_some_resource() is slow, to avoid calling it for each test use setUpClass()
            and store the result as class variable
        """
        super(TestInputOutput, cls).setUpClass()

        # delete old repository
        delete_repo(TEST_DIR, "Catan_Test")

        cls.hexagons = init_hexagons()

        # check if there is already a game around
        try:
            repo = Repo(os.path.join(TEST_DIR, "Catan_Test"))
            init_state = get_initial_phase(repo)
        except NoSuchPathError:
            init_state = None

        # only initialize git and the points if no init state around
        if init_state is None:
            cls.settlement_points = init_settlement_points(cls.hexagons)
            cls.road_points = init_road_points(cls.hexagons)
            cls.repo = create_git_dir_test()
            # initialize map and git folders
            initialize_game_state(cls.repo, cls.settlement_points, cls.road_points, "Red")


    def testLongestRoadStraight(self):
        roads = [
            (15,22),
            (15,23),
            (16,23),
            (16,24),
            (17,24)
        ]

        changed = []

        for rp in self.road_points:
            tuple = (list(rp.coords)[0].id, list(rp.coords)[1].id)
            tuple_rev = (list(rp.coords)[1].id, list(rp.coords)[0].id)
            if tuple in roads or tuple_rev in roads:
                update_road_point(self.repo, rp.index, "Red")
                changed.append(rp)

        hlr = has_longest_road(self.repo, 0, self.hexagons)

        self.assertEqual(hlr, True)

        for rp in changed:
            update_road_point(self.repo, rp.index, "Bot")

    def testLongestRoadDoubleNeighbour(self):
        roads = [
            (15,22),
            (15,23),
            (16,23),
            (16,24),
            (22,23),
        ]

        changed = []

        for rp in self.road_points:
            tuple = (list(rp.coords)[0].id, list(rp.coords)[1].id)
            tuple_rev = (list(rp.coords)[1].id, list(rp.coords)[0].id)
            if tuple in roads or tuple_rev in roads:
                update_road_point(self.repo, rp.index, "Red")
                changed.append(rp)

        hlr = has_longest_road(self.repo, 0, self.hexagons)

        self.assertEqual(hlr, False)

        for rp in changed:
            update_road_point(self.repo, rp.index, "Bot")


    def testLongestRoadTrippleNeighbour(self):
            roads = [
                (14,15),
                (15,22),
                (15,23),
                (16,23),
                (16,24),
                (22,23),
                (23,29),
                (29,30),
            ]

            changed = []

            for rp in self.road_points:
                tuple = (list(rp.coords)[0].id, list(rp.coords)[1].id)
                tuple_rev = (list(rp.coords)[1].id, list(rp.coords)[0].id)
                if tuple in roads or tuple_rev in roads:
                    update_road_point(self.repo, rp.index, "Red")
                    changed.append(rp)

            hlr = has_longest_road(self.repo, 0, self.hexagons)

            self.assertEqual(hlr, True)

            for rp in changed:
                update_road_point(self.repo, rp.index, "Bot")

    def testLongestRoadError(self):
            roads = [
                (22,15),
                (22,23),
                (29,22),
                (24,23),
                (29,23),
                (30,23),
                (44,38),
                (45,38),
                (46,39),
            ]
            changed = []

            for rp in self.road_points:
                tuple = (list(rp.coords)[0].id, list(rp.coords)[1].id)
                tuple_rev = (list(rp.coords)[1].id, list(rp.coords)[0].id)
                if tuple in roads or tuple_rev in roads:
                    update_road_point(self.repo, rp.index, "Red")
                    changed.append(rp)

            hlr = has_longest_road(self.repo, 0, self.hexagons)

            self.assertEqual(hlr, True)

            for rp in changed:
                update_road_point(self.repo, rp.index, "Bot")
