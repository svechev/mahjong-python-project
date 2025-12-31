import unittest

from game.tiles import Suit, Tile, tile_from_str, all_tiles, winds
from random import shuffle

# todo write some more tests


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



