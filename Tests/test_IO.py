import os
from unittest import TestCase

from git import Repo, NoSuchPathError, repo

from Tests.test_utils import delete_repo
from UI import init_settlement_points, init_road_points, init_hexagons
from gloabl_definitions import TEST_DIR
from initializing import initialize_game_state
from utils import (
    get_initial_phase,
    update_initial_phase,
    get_initial_active_player,
    update_initial_active_player,
    get_active_player,
    update_active_player,
    get_turn_phase,
    update_turn_phase,
    get_player_hand,
    update_player_hand,
    get_player_buildings,
    get_player_buildings_type,
    update_player_buildings,
    get_bank_resources,
    update_bank_resources,
    get_bank_development_cards,
    update_bank_development_cards,
    get_discard_pile,
    update_discard_pile,
    get_bandit,
    update_bandit,
    get_all_settlement_points,
    get_settlement_point,
    update_settlement_point,
    get_all_road_points,
    get_road_point,
    update_road_point,
    create_git_dir_test
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


    def testGetWharfType(self):
        return NotImplementedError()
    def testGetInitialPhase(self):
        phase = get_initial_phase(self.repo)
        self.assertEqual("phase_one", phase)

    def testUpdateInitialPhase(self):
        update_initial_phase(self.repo)
        phase = get_initial_phase(self.repo)
        self.assertEqual("phase_two", phase)

    def testGetInitialActivePlayer(self):
        ap = get_initial_active_player(self.repo)
        self.assertEqual(0, ap)

    def testUpdateInitialActivePlayer(self):
        update_initial_active_player(self.repo)
        ap = get_initial_active_player(self.repo)
        self.assertEqual(1, ap)

        update_initial_active_player(self.repo)
        update_initial_active_player(self.repo)
        ap = get_initial_active_player(self.repo)
        self.assertEqual(3, ap)

        update_initial_active_player(self.repo)
        ap = get_initial_active_player(self.repo)
        self.assertEqual(0, ap)

    def testGetActivePlayer(self):
        ap = get_active_player(self.repo)
        self.assertEqual(0, ap)

    def testUpdateActivePlayer(self):
        update_active_player(self.repo)
        ap = get_active_player(self.repo)
        self.assertEqual(1, ap)

        update_active_player(self.repo)
        update_active_player(self.repo)
        ap = get_active_player(self.repo)
        self.assertEqual(3, ap)

        update_active_player(self.repo)
        ap = get_active_player(self.repo)
        self.assertEqual(0, ap)

    def testGetTurnPhase(self):
        tp = get_turn_phase(self.repo)
        self.assertEqual("bot", tp)

    def testUpdateTurnPhase(self):
        update_turn_phase(self.repo)
        tp = get_turn_phase(self.repo)
        self.assertEqual("dice_roll", tp)

        update_turn_phase(self.repo)
        tp = get_turn_phase(self.repo)
        self.assertEqual("trading", tp)

        update_turn_phase(self.repo)
        tp = get_turn_phase(self.repo)
        self.assertEqual("building", tp)

        update_turn_phase(self.repo)
        tp = get_turn_phase(self.repo)
        self.assertEqual("dice_roll", tp)

    def testGetPlayerHand(self):
        rc = get_player_hand(self.repo, "resource_cards", 0)
        bc = get_player_hand(self.repo, "bought_cards", 0)
        ac = get_player_hand(self.repo, "available_cards", 1)
        uc = get_player_hand(self.repo, "unveiled_cards", 1)

        self.assertEqual([0, 0, 0, 0, 0], rc)
        self.assertEqual([0, 0, 0, 0], bc)
        self.assertEqual([0, 0, 0, 0], ac)
        self.assertEqual([0, 0], uc)

    def testUpdatePlayerHand(self):
        # RESOURCE CARDS
        # add to a player's hand
        update_player_hand(self.repo, "resource_cards", 0, [1,2,3,4,5])
        rc = get_player_hand(self.repo, "resource_cards", 0)
        self.assertCountEqual([1,2,3,4,5], rc)

        # remove cards from a player's hand
        update_player_hand(self.repo, "resource_cards", 0, [-1,0,-3,0,-5])
        rc = get_player_hand(self.repo, "resource_cards", 0)
        self.assertCountEqual([0,2,0,4,0], rc)

        # illegal numbers in update
        update_player_hand(self.repo, "resource_cards", 0, [20,0,1,1,1])
        rc = get_player_hand(self.repo, "resource_cards", 0)
        self.assertCountEqual([0,2,0,4,0], rc)

        update_player_hand(self.repo, "resource_cards", 0, [0,0,0,-5,0])
        rc = get_player_hand(self.repo, "resource_cards", 0)
        self.assertCountEqual([0,2,0,4,0], rc)

        # DEVELOPMENT CARDS
        update_player_hand(self.repo, "bought_cards", 0, [1,1,1,5])
        bc = get_player_hand(self.repo, "bought_cards", 0)
        self.assertCountEqual([1,1,1,5], bc)

        update_player_hand(self.repo, "bought_cards", 0, [0,-1,0,0])
        bc = get_player_hand(self.repo, "bought_cards", 0)
        self.assertCountEqual([1,0,1,5], bc)

        update_player_hand(self.repo, "bought_cards", 0, [4,1,1,5])
        bc = get_player_hand(self.repo, "bought_cards", 0)
        self.assertCountEqual([1,0,1,5], bc)

        update_player_hand(self.repo, "bought_cards", 0, [-4,1,1,5])
        bc = get_player_hand(self.repo, "bought_cards", 0)
        self.assertCountEqual([1,0,1,5], bc)


        update_player_hand(self.repo, "unveiled_cards", 0, [1,2])
        uc = get_player_hand(self.repo, "unveiled_cards", 0)
        self.assertCountEqual([1,2], uc)

        update_player_hand(self.repo, "unveiled_cards", 0, [0,5])
        uc = get_player_hand(self.repo, "unveiled_cards", 0)
        self.assertCountEqual([1,2], uc)

        update_player_hand(self.repo, "unveiled_cards", 0, [-7,0])
        uc = get_player_hand(self.repo, "unveiled_cards", 0)
        self.assertCountEqual([1,2], uc)

    def testGetPlayerBuildings(self):
        buildings = get_player_buildings(self.repo, 0)
        roads = get_player_buildings_type(self.repo, "Road", 0 )
        villages = get_player_buildings_type(self.repo, "Village", 0 )
        cities = get_player_buildings_type(self.repo, "City", 0 )

        self.assertEqual([roads, villages, cities], buildings)
        self.assertEqual([15, 5, 4], buildings)

    def testUpdatePlayerBuildings(self):
        update_player_buildings(self.repo, 0, [-1,0,0])
        buildings = get_player_buildings(self.repo, 0)
        self.assertEqual([14, 5, 4], buildings)

        update_player_buildings(self.repo, 0, [2,0,0])
        buildings = get_player_buildings(self.repo, 0)
        self.assertEqual([14, 5, 4], buildings)

    def testGetBankResources(self):
        bnk = get_bank_resources(self.repo)
        self.assertEqual([19,19,19,19,19], bnk)

    def testUpdateBankResources(self):

        update_bank_resources(self.repo, [-1,0,0,0,0])
        bnk = get_bank_resources(self.repo)
        self.assertEqual([18,19,19,19,19], bnk)

        update_bank_resources(self.repo, [2,0,0,0,0])
        bnk = get_bank_resources(self.repo)
        self.assertEqual([18,19,19,19,19], bnk)

        update_bank_resources(self.repo, [-20,0,0,0,0])
        bnk = get_bank_resources(self.repo)
        self.assertEqual([18,19,19,19,19], bnk)

        update_bank_resources(self.repo, [-1,-2,-2,-2,-2])
        bnk = get_bank_resources(self.repo)
        self.assertEqual([17,17,17,17,17], bnk)

    def testGetBankDevCards(self):
        bnk = get_bank_development_cards(self.repo)
        self.assertEqual([2,2,2,14,5], bnk)

    def testUpdateBankDevCards(self):
        update_bank_development_cards(self.repo, [-1,0,0,0,0])
        bnk = get_bank_development_cards(self.repo)
        self.assertEqual([1,2,2,14,5], bnk)

        update_bank_development_cards(self.repo, [3,0,0,0,0])
        bnk = get_bank_development_cards(self.repo)
        self.assertEqual([1,2,2,14,5], bnk)

        update_bank_development_cards(self.repo, [-2,0,0,0,0])
        bnk = get_bank_development_cards(self.repo)
        self.assertEqual([1,2,2,14,5], bnk)

        update_bank_development_cards(self.repo, [-1,-2,-2,-2,-2])
        bnk = get_bank_development_cards(self.repo)
        self.assertEqual([0,0,0,12,3], bnk)

    def testGetDiscardPile(self):
        dp = get_discard_pile(self.repo)
        self.assertEqual([0,0,0], dp)

    def testUpdateDiscardPile(self):
        update_discard_pile(self.repo, [1,1,1])
        dp = get_discard_pile(self.repo)
        self.assertEqual([1,1,1], dp)

        update_discard_pile(self.repo, [-2,1,1])
        dp = get_discard_pile(self.repo)
        self.assertEqual([1,1,1], dp)

    def testGetBandit(self):
        b = get_bandit(self.repo, self.hexagons)
        self.assertEqual(self.hexagons[24], b)

    def testUpdateBandit(self):
        update_bandit(self.repo, self.hexagons, 26)
        b = get_bandit(self.repo, self.hexagons)
        self.assertEqual(self.hexagons[26], b)
        update_bandit(self.repo, self.hexagons, 3)
        b = get_bandit(self.repo, self.hexagons)
        self.assertEqual(self.hexagons[26], b)

    def testAllSettlementPoints(self):
        sps = get_all_settlement_points(self.repo, self.hexagons)

        coords = [sp.coords for sp in sps]
        coords_expected = [rp.coords for rp in self.settlement_points]
        self.assertCountEqual(coords, coords_expected)

        owner = [sp.owner for sp in sps]
        owner_expected = [sp.owner for sp in self.settlement_points]
        self.assertCountEqual(owner, owner_expected)

        settlement_type = [sp.coords for sp in sps]
        settlement_type_expected = [sp.coords for sp in self.settlement_points]
        self.assertCountEqual(settlement_type_expected, settlement_type)

    def testGetSettlementPoint(self):
        sp = get_settlement_point(self.repo, 24, self.hexagons)
        self.assertEqual(sp.coords, self.settlement_points[24].coords)
        self.assertEqual(sp.owner, self.settlement_points[24].owner)
        self.assertEqual(self.settlement_points[24].type, sp.type)

    def testUpdateSettlementPoint(self):
        sps = get_all_settlement_points(self.repo, self.hexagons)
        for sp in sps:
            update_settlement_point(self.repo, sp.index, "Red", "Village")
            nsp = get_settlement_point(self.repo, sp.index, self.hexagons)
            self.assertEqual("Red", nsp.owner)
            self.assertEqual("Village", nsp.type)
        for sp in sps:
            update_settlement_point(self.repo, sp.index, "Red", "City")
            nsp = get_settlement_point(self.repo, sp.index, self.hexagons)
            self.assertEqual("Red", nsp.owner)
            self.assertEqual("City", nsp.type)

    def testAllRoadPoint(self):
        rps = get_all_road_points(self.repo, self.hexagons)
        coords = [rp.coords for rp in rps]
        coords_expected = [rp.coords for rp in self.road_points]
        self.assertCountEqual(coords_expected, coords)

        owner = [rp.owner for rp in rps]
        owner_expected = [rp.owner for rp in self.road_points]
        self.assertCountEqual(owner_expected, owner)

    def testGetRoadPoint(self):
        rp = get_road_point(self.repo, 24, self.hexagons)
        self.assertEqual(self.road_points[24].coords, rp.coords)
        self.assertEqual(self.road_points[24].owner, rp.owner)

    def testUpdateRoadPoint(self):
        update_road_point(self.repo, 24, "Red")
        rp = get_road_point(self.repo, 24, self.hexagons)
        self.assertEqual("Red", rp.owner)