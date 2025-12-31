from __future__ import annotations
from enum import Enum
from functools import total_ordering
from typing import List

winds = ["North", "East", "South", "West"]
dragons = ["White", "Green", "Red"]
suit_order = ['M', 'P', 'S', "Wind", "Dragon"]


class Suit(Enum):
    MAN = 'M'
    PIN = 'P'
    SOU = 'S'
    WIND = "Wind"
    DRAGON = "Dragon"

    @staticmethod
    def dragon_tile_dora(indicator: str) -> str:
        return dragons[(dragons.index(indicator) + 1) % 3]

    @staticmethod
    def wind_tile_dora(indicator: str) -> str:
        return winds[(winds.index(indicator) + 1) % 3]


@total_ordering
class Tile:
    def __init__(self, suit: Suit, value: str | int, is_red_five: bool = False) -> None:
        self._suit = suit
        self._value = value
        self._red_five = is_red_five

    @property
    def suit(self) -> Suit:
        return self._suit

    @property
    def value(self) -> str | int:
        return self._value

    @property
    def red_five(self) -> bool:
        return self._red_five

    def __str__(self) -> str:
        if self.suit in [Suit.WIND, Suit.DRAGON]:
            return f"{self.value}"
        else:
            if self.red_five:
                return f"{self.suit.value}{self.value}*"
            else:
                return f"{self.suit.value}{self.value}"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash(self.suit) + hash(self.value)

    def __eq__(self, other: Tile) -> bool:
        return self.suit == other.suit and self.value == other.value and self.red_five == other.red_five

    def __lt__(self, other: Tile) -> bool:
        suit1, suit2 = suit_order.index(self.suit.value), suit_order.index(other.suit.value)
        if suit1 == suit2:
            if suit1 == suit_order.index("Wind"):
                return winds.index(self.value) < winds.index(other.value)
            elif suit1 == suit_order.index("Dragon"):
                return dragons.index(self.value) < dragons.index(other.value)
            else:
                if self.value == other.value == 5:
                    return not self.red_five and other.red_five
                return self.value < other.value
        elif suit1 < suit2:
            return True
        else:
            return False

    def is_honour(self) -> bool:
        return self.suit in [Suit.WIND, Suit.DRAGON]

    def is_terminal(self) -> bool:
        return not self.is_honour() and (self.value == 1 or self.value == 9)

    def dora(self) -> Tile:  # if self is the indicator, the result is the dora
        dora_suit = self.suit
        if dora_suit == Suit.WIND:
            dora_value = Suit.wind_tile_dora(self.value)
        elif dora_suit == Suit.DRAGON:
            dora_value = Suit.dragon_tile_dora(self.value)
        else:
            dora_value = self.value + 1
            if dora_value == 10:
                dora_value = 1
        return Tile(dora_suit, dora_value)


def consecutive(first: Tile, second: Tile) -> bool:
    return first.suit not in [Suit.WIND, Suit.DRAGON] and first.suit == second.suit and second.value == first.value + 1


def remove_red_fives(hand: List[Tile]) -> List[Suit]:
    removed = []
    for i, tile in enumerate(hand):
        if tile.red_five:
            hand[i] = Tile(tile.suit, tile.value)
            removed.append(tile.suit)
    return removed


def add_red_fives(hand: List[Tile], to_add: List[Suit]):
    for i, tile in enumerate(hand):
        if tile.suit in to_add and tile.value == 5:
            hand[i] = Tile(tile.suit, 5, is_red_five=True)
            to_add.remove(tile.suit)


def split_hand(hand: List[Tile]) -> (List[Tile], List[Tile], List[Tile], List[Tile]):
    m_tiles = [tile for tile in hand if tile.suit == Suit.MAN]
    p_tiles = [tile for tile in hand if tile.suit == Suit.PIN]
    s_tiles = [tile for tile in hand if tile.suit == Suit.SOU]
    honour_tiles = [tile for tile in hand if tile not in [*m_tiles, *p_tiles, *s_tiles]]
    return m_tiles, p_tiles, s_tiles, honour_tiles


def tile_from_str(st: str) -> Tile | None:
    if len(st) < 2:
        return None
    if st in dragons:
        return Tile(Suit.DRAGON, st)
    if st in winds:
        return Tile(Suit.WIND, st)
    if 2 <= len(st) <= 3:
        if st[0] in ['M', 'P', 'S'] and st[1].isnumeric() and 1 <= int(st[1]) <= 9:
            match st[0]:
                case 'M':
                    suit = Suit.MAN
                case 'P':
                    suit = Suit.PIN
                case 'S':
                    suit = Suit.SOU
            if len(st) == 2:
                return Tile(suit, int(st[1]))
            if len(st) == 3 and int(st[1]) == 5 and st[2] == '*':
                return Tile(suit, 5, is_red_five=True)
    return None


def print_hand(hand: List[Tile], kan_tiles: List[Tile]):
    m_tiles, p_tiles, s_tiles, honour_tiles = split_hand(hand)
    print(f"Hand: {m_tiles}, {p_tiles}, {s_tiles}, {honour_tiles}    Kan:", end=' ')
    for tile in kan_tiles:
        if tile.value == 5:
            tiles = [tile for _ in range(3)] + [Tile(tile.suit, 5, is_red_five=True)]
            print(f"{tiles}")
        else:
            print(f"{[tile for _ in range(4)]}")
    print()


man_tiles = [Tile(Suit.MAN, i) for i in range(1, 10)]
man_copies = man_tiles * 4
man_copies[4] = Tile(Suit.MAN, 5, is_red_five=True)


pin_tiles = [Tile(Suit.PIN, i) for i in range(1, 10)]
pin_copies = pin_tiles * 4
pin_copies[4] = Tile(Suit.PIN, 5, is_red_five=True)

sou_tiles = [Tile(Suit.SOU, i) for i in range(1, 10)]
sou_copies = sou_tiles * 4
sou_copies[4] = Tile(Suit.SOU, 5, is_red_five=True)

wind_tiles = [Tile(Suit.WIND, wind) for wind in winds]
wind_copies = wind_tiles*4
dragon_tiles = [Tile(Suit.DRAGON, dragon) for dragon in dragons]
dragon_copies = dragon_tiles*4

all_tiles = [*man_tiles, *pin_tiles, *sou_tiles, *wind_tiles, *dragon_tiles]
all_copies = [*man_copies, *pin_copies, *sou_copies, *wind_copies, *dragon_copies]




