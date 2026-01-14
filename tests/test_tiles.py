import unittest

from src.logic.tile import *
from random import shuffle

# todo write some more tests

suits = [Suit.MAN, Suit.PIN, Suit.SOU, Suit.WIND, Suit.DRAGON]
num_suits = suits[:3]
honor_suits = suits[3:]


class TileTests(unittest.TestCase):
    def test_01_tile_from_str(self):
        # Arrange
        st = "m1"
        st = st.lower().capitalize()
        self.assertTrue(st == "M1")

        # Act
        tile = tile_from_str(st)
        tile2 = Tile(Suit.MAN, 1)

        # Assert
        self.assertTrue(tile == tile2)

    def test_02_tile_order(self):
        # Arrange
        tiles = list(all_tiles)

        # Act
        shuffle(tiles)
        tiles.sort()

        # Assert
        self.assertTrue(tiles == all_tiles)

    def test_03_compare_red_five(self):
        # Arrenge
        tile5 = Tile(Suit.MAN, 5)
        red5 = Tile(Suit.MAN, 5, is_red_five=True)
        tile6 = Tile(Suit.MAN, 6)

        # Act/Assert
        self.assertTrue(tile5 < red5 < tile6)

    def test_04_dora(self):
        pass

    def test_05_remove_and_add_red_fives(self):
        # Arrenge
        tile5 = Tile(Suit.MAN, 5)
        red5 = Tile(Suit.MAN, 5, is_red_five=True)
        tile6 = Tile(Suit.MAN, 6)

        hand = [Tile(suit, 5, is_red_five=True) for suit in num_suits]

        # Act
        has_red_fives = [True if tile.red_five else False for tile in hand]

        removed = remove_red_fives(hand)
        removed_correctly = [True if tile.red_five else False for tile in hand]

        add_red_fives(hand, removed)
        has_red_fives_again = [True if tile.red_five else False for tile in hand]

        # Assert
        self.assertTrue(False not in has_red_fives)
        self.assertTrue(len(has_red_fives) == 3)

        self.assertTrue(True not in removed_correctly)
        self.assertTrue(len(removed_correctly) == 3)

        self.assertTrue(False not in has_red_fives_again)
        self.assertTrue(len(has_red_fives_again) == 3)



