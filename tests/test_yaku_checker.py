import unittest

from src.logic.tile import Suit, Tile, all_tiles
from src.rules.winning_hand import get_yakus, discard_for_ready_hand, ready_hand

PREVALENT_WIND = "East"
seat_wind = "South"


class YakuTests(unittest.TestCase):
    def test_01_triplets(self):
        # Arrange
        hand = [Tile(Suit.MAN, 3) for _ in range(3)] + [Tile(Suit.MAN, 4) for _ in range(3)]
        hand += [Tile(Suit.SOU, 4) for _ in range(3)]
        hand += [Tile(Suit.SOU, 9) for _ in range(2)]

        kan_tiles = [Tile(Suit.PIN, 4)]
        # Act
        closed_yakus = get_yakus(hand, kan_tiles, PREVALENT_WIND, seat_wind, [], hand[0], num_waits=2)

        open_combos = [hand[:3]]
        hand = hand[3:]

        open_yakus_tsumo = get_yakus(hand, kan_tiles, PREVALENT_WIND, seat_wind, open_combos, hand[4],
                                     num_waits=2,
                                     is_ron=False)
        open_yakus_ron = get_yakus(hand, kan_tiles, PREVALENT_WIND, seat_wind, open_combos, hand[4],
                                   num_waits=2,
                                   is_ron=True)

        # Assert
        self.assertTrue("Tsumo" in closed_yakus)
        self.assertTrue("All triplets" in closed_yakus)
        self.assertTrue("Triple triplets" in closed_yakus)
        self.assertTrue("Four concealed triplets" in closed_yakus)
        self.assertTrue(len(closed_yakus) == 4)
        self.assertTrue("Three concealed triplets" in open_yakus_tsumo)
        self.assertTrue(len(open_yakus_tsumo) == 3)
        self.assertTrue("Three concealed triplets" not in open_yakus_ron)
        self.assertTrue(len(open_yakus_ron) == 2)

    def test_02_all_simples(self):
        # Arrange
        hand = [Tile(Suit.MAN, i) for i in range(3, 6)] + [Tile(Suit.MAN, 4) for _ in range(3)]
        hand += [Tile(Suit.PIN, 4) for _ in range(2)]
        hand += [Tile(Suit.SOU, 2) for _ in range(3)]
        hand += [Tile(Suit.SOU, 8) for _ in range(3)]
        open_combos = [hand[-3:]]
        hand = hand[:-3]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, open_combos, hand[0])

        # Assert
        self.assertTrue("Tsumo" not in yakus)
        self.assertTrue("All simples" in yakus)
        self.assertTrue(len(yakus) == 1)

    def test_03_pinfu(self):
        # Arrange
        hand = [Tile(Suit.MAN, i) for i in range(3, 6)]
        hand += [Tile(Suit.MAN, i) for i in range(4, 7)]
        hand += [Tile(Suit.PIN, i) for i in range(4, 7)]
        hand += [Tile(Suit.SOU, i) for i in range(2, 5)]
        hand += [Tile(Suit.WIND, "North") for _ in range(2)]
        hand.sort()
        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[0])  # draw a tile at start of sequence
        yakus2 = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[13])  # draw the "pair" tile
        yakus3 = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[1])  # same as case 1, but with overlap
        yakus4 = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[10])  # draw middle tile of sequence
        yakus5 = get_yakus(hand, [], PREVALENT_WIND, "North", [], hand[0])  # pair is "yakuhai" tile

        # Assert
        self.assertTrue("Pinfu" in yakus)
        self.assertTrue("Pinfu" not in yakus2)
        self.assertTrue("Pinfu" in yakus3)
        self.assertTrue("Pinfu" not in yakus4)
        self.assertTrue("Pinfu" not in yakus5)

    def test_04_seven_pairs(self):
        # Arrange
        hand = [Tile(Suit.MAN, 9) for _ in range(2)]
        hand += [Tile(Suit.PIN, 5)] + [Tile(Suit.PIN, 5, is_red_five=True)]
        hand += [Tile(Suit.SOU, 2) for _ in range(2)]
        hand += [Tile(Suit.SOU, 4) for _ in range(2)]
        hand += [Tile(Suit.SOU, 5)] + [Tile(Suit.SOU, 5, is_red_five=True)]
        hand += [Tile(Suit.WIND, "West") for _ in range(2)]
        hand += [Tile(Suit.DRAGON, "Red") for _ in range(2)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[9])
        # Assert
        self.assertTrue("Seven pairs" in yakus)
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue(len(yakus) == 2)

    def test_05_half_flush(self):
        # Arrange
        hand = [Tile(Suit.MAN, 1) for _ in range(3)]
        hand += [Tile(Suit.MAN, 4) for _ in range(3)]
        hand += [Tile(Suit.MAN, i) for i in range(5, 8)]
        hand += [Tile(Suit.MAN, 9) for _ in range(3)]
        hand += [Tile(Suit.DRAGON, "White") for _ in range(2)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Half flush" in yakus)

    def test_06_full_flush(self):
        # Arrange
        hand = [Tile(Suit.MAN, 2) for _ in range(3)]
        hand += [Tile(Suit.MAN, 3) for _ in range(2)]
        hand += [Tile(Suit.MAN, 4) for _ in range(3)]
        hand += [Tile(Suit.MAN, i) for i in range(5, 8)]
        hand += [Tile(Suit.MAN, 7) for _ in range(3)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Full flush" in yakus)
        self.assertTrue("All simples" in yakus)

    def test_07_dragons(self):
        # Arrange
        hand = [Tile(Suit.MAN, 1) for _ in range(3)]
        hand += [Tile(Suit.MAN, 4) for _ in range(2)]
        hand += [Tile(Suit.DRAGON, "White") for _ in range(3)]
        hand += [Tile(Suit.DRAGON, "Green") for _ in range(3)]
        hand += [Tile(Suit.DRAGON, "Red") for _ in range(3)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Half flush" in yakus)
        self.assertTrue("All triplets" in yakus)
        self.assertTrue("White dragon" in yakus)
        self.assertTrue("Red dragon" in yakus)
        self.assertTrue("Green dragon" in yakus)
        self.assertTrue("Big three dragons" in yakus)

    def test_08_big_winds(self):
        # Arrange
        hand = [Tile(Suit.DRAGON, "Red") for _ in range(2)]
        hand += [Tile(Suit.WIND, "East") for _ in range(3)]
        hand += [Tile(Suit.WIND, "South") for _ in range(3)]
        hand += [Tile(Suit.WIND, "West") for _ in range(3)]
        hand += [Tile(Suit.WIND, "North") for _ in range(3)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("All honors" in yakus)
        self.assertTrue("All triplets" in yakus)
        self.assertTrue("Prevalent wind" in yakus)
        self.assertTrue("Seat wind" in yakus)
        self.assertTrue("Four big winds" in yakus)
        self.assertTrue("Half outside hand" in yakus)

    def test_09_little_winds(self):
        # Arrange
        hand = [Tile(Suit.MAN, 1) for _ in range(3)]
        hand += [Tile(Suit.WIND, "East") for _ in range(2)]
        hand += [Tile(Suit.WIND, "South") for _ in range(3)]
        hand += [Tile(Suit.WIND, "West") for _ in range(3)]
        hand += [Tile(Suit.WIND, "North") for _ in range(3)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Half outside hand" in yakus)
        self.assertTrue("All terminals and honors" in yakus)
        self.assertTrue("All triplets" in yakus)
        self.assertTrue("Seat wind" in yakus)
        self.assertTrue("Four little winds" in yakus)
        self.assertTrue("Half flush" in yakus)

    def test_10_sequences(self):
        # Arrange
        hand = [Tile(Suit.MAN, i) for i in range(1, 4)]
        hand += [Tile(Suit.MAN, i) for i in range(1, 4)]
        hand += [Tile(Suit.MAN, 9) for _ in range(2)]
        hand += [Tile(Suit.PIN, i) for i in range(1, 4)]
        hand += [Tile(Suit.SOU, i) for i in range(1, 4)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[1])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Fully outside hand" in yakus)
        self.assertTrue("Mixed triple sequence" in yakus)
        self.assertTrue("Pure double sequence" in yakus)
        self.assertTrue(len(yakus) == 4)

    def test_11_twice_pure_double_sequence(self):
        # Arrange
        hand = [Tile(Suit.MAN, 2) for _ in range(2)]
        hand += [Tile(Suit.MAN, 3) for _ in range(2)]
        hand += [Tile(Suit.MAN, 4) for _ in range(2)]
        hand += [Tile(Suit.SOU, 2) for _ in range(2)]
        hand += [Tile(Suit.SOU, 3) for _ in range(2)]
        hand += [Tile(Suit.SOU, 4) for _ in range(2)]
        hand += [Tile(Suit.DRAGON, "Green") for _ in range(2)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Twice pure double sequence" in yakus)
        self.assertTrue(len(yakus) == 2)

    def test_12_thirteen_orphans(self):
        # Arrange
        hand = [tile for tile in all_tiles if tile.is_honour() or tile.is_terminal()]
        hand.append(Tile(Suit.DRAGON, "Red"))

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], last_draw=hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Thirteen orphans" in yakus)
        self.assertTrue(len(yakus) == 2)

    def test_13_wait_thirteen_orphans(self):
        # Arrange
        hand = [tile for tile in all_tiles if tile.is_honour() or tile.is_terminal()]
        hand.append(Tile(Suit.DRAGON, "Red"))

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], last_draw=hand[13])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Thirteen-wait thirteen orphans" in yakus)
        self.assertTrue(len(yakus) == 2)

    def test_14_all_green(self):
        # Arrange
        hand = [Tile(Suit.SOU, 2) for _ in range(2)]
        hand += [Tile(Suit.SOU, 3) for _ in range(2)]
        hand += [Tile(Suit.SOU, 4) for _ in range(2)]
        hand += [Tile(Suit.SOU, 6) for _ in range(3)]
        hand += [Tile(Suit.SOU, 8) for _ in range(2)]
        hand += [Tile(Suit.DRAGON, "Green") for _ in range(3)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], last_draw=hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("All green" in yakus)
        self.assertTrue("Half flush" in yakus)
        self.assertTrue("Pure double sequence" in yakus)
        self.assertTrue("Green dragon" in yakus)
        self.assertTrue(len(yakus) == 5)

    def test_15_complex_case(self):
        # Arrange
        hand = [Tile(Suit.MAN, i) for i in range(7, 10)]
        hand += [Tile(Suit.SOU, 5, is_red_five=True)]
        hand += [Tile(Suit.SOU, 5) for _ in range(2)]
        hand += [Tile(Suit.SOU, 6) for _ in range(2)]
        hand += [Tile(Suit.SOU, 7) for _ in range(2)]
        hand += [Tile(Suit.SOU, 8)]
        hand += [Tile(Suit.DRAGON, "Green") for _ in range(3)]

        # Act
        yakus = get_yakus(hand, [], PREVALENT_WIND, seat_wind, [], last_draw=hand[0])

        # Assert
        self.assertTrue("Tsumo" in yakus)
        self.assertTrue("Green dragon" in yakus)
        self.assertTrue(len(yakus) == 2)

    def test_16_discard_for_ready_hand(self):
        # Arrange
        hand = [Tile(Suit.MAN, i) for i in range(7, 10)]
        hand += [Tile(Suit.SOU, 5, is_red_five=True)]
        hand += [Tile(Suit.SOU, 5) for _ in range(2)]
        hand += [Tile(Suit.SOU, 6) for _ in range(2)]
        hand += [Tile(Suit.SOU, 7) for _ in range(2)]
        hand += [Tile(Suit.SOU, 8)]
        hand += [Tile(Suit.DRAGON, "Green") for _ in range(2)]
        hand += [Tile(Suit.DRAGON, "Red")]
        actual_discard = [Tile(Suit.DRAGON, "Red")]

        # Act
        to_discard = discard_for_ready_hand(hand, [], PREVALENT_WIND, seat_wind, [])

        # Assert
        self.assertTrue(actual_discard == to_discard)

    def test_17_ready_hand(self):
        # Arrange
        # Arrange
        hand = [Tile(Suit.MAN, 9) for _ in range(2)]
        hand += [Tile(Suit.PIN, 5)] + [Tile(Suit.PIN, 5, is_red_five=True)]
        hand += [Tile(Suit.SOU, 2) for _ in range(2)]
        hand += [Tile(Suit.SOU, 4) for _ in range(2)]
        hand += [Tile(Suit.SOU, 5)] + [Tile(Suit.SOU, 5, is_red_five=True)]
        hand += [Tile(Suit.WIND, "West") for _ in range(2)]
        hand += [Tile(Suit.DRAGON, "Red")]

        actual_waits = [Tile(Suit.DRAGON, "Red")]
        # Act
        waits = ready_hand(hand, [], PREVALENT_WIND, seat_wind, [])

        # Assert
        self.assertTrue(waits == actual_waits)
