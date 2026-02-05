import unittest

from src.logic.tile import *
from random import shuffle

suits = [Suit.MAN, Suit.PIN, Suit.SOU, Suit.WIND, Suit.DRAGON]
num_suits = suits[:3]
honor_suits = suits[3:]


class TileTests(unittest.TestCase):
    def test_01_dora(self) -> None:
        # Arrange
        checks: list[list[None | bool]] = [[None] * 9 for _ in range(3)] + [[None] * 4, [None] * 3]
        list_of_trues = [[True] * 9 for _ in range(3)] + [[True] * 4, [True] * 3]
        amount_of_checks = [9, 9, 9, 4, 3]
        tiles_to_check = [man_tiles, pin_tiles, sou_tiles, wind_tiles, dragon_tiles]

        # Act
        for i in range(5):
            for j in range(amount_of_checks[i]):
                current_suit = tiles_to_check[i]
                new_tile = current_suit[j].dora()
                next_index = (j + 1) % len(current_suit)
                if new_tile == current_suit[next_index]:
                    checks[i][j] = True
                else:
                    checks[i][j] = False

        # Assert
        self.assertTrue(checks == list_of_trues)

    def test_02_tile_order(self) -> None:
        # Arrange
        tiles = list(all_tiles)

        # Act
        shuffle(tiles)
        tiles.sort()

        # Assert
        self.assertTrue(tiles == all_tiles)

    def test_03_compare_red_five(self) -> None:
        # Arrange
        tile5 = Tile(Suit.MAN, 5)
        red5 = Tile(Suit.MAN, 5, is_red_five=True)
        tile6 = Tile(Suit.MAN, 6)

        # Act/Assert
        self.assertTrue(tile5 < red5 < tile6)

    def test_04_remove_and_add_red_fives(self) -> None:
        # Arrange
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
