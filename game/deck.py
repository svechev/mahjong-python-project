from game.tiles import Tile, all_copies, tile_from_str
from random import shuffle
from typing import List


class Deck:
    def __init__(self):
        self.wall = all_copies
        for _ in range(5):
            shuffle(self.wall)

        self.open_dora, self.closed_dora = self.get_dora_indicators()

        self.dora_tiles_count = 1
        self.draws_left = 75
        live_tiles_count = self.draws_left + 13
        self.dead_wall, self.wall = self.wall[live_tiles_count:], self.wall[:live_tiles_count]

    def get_dora_indicators(self) -> (List[Tile], List[Tile]):
        open_dora_tiles, closed_dora_tiles = self.wall[:5], self.wall[5:10]
        self.wall = self.wall[10:]
        return open_dora_tiles, closed_dora_tiles

    def get_starting_hand(self) -> List[Tile]:
        starting_hand = self.wall[:13]
        self.wall = self.wall[13:]
        starting_hand.sort()
        return starting_hand

    def draw(self, dead_wall=False) -> Tile:
        if dead_wall:
            tile = self.dead_wall[0]
            self.dead_wall = self.dead_wall[1:]
        else:
            tile = self.wall[0]
            self.wall = self.wall[1:]
        self.draws_left -= 1
        return tile


def discard(hand: List[Tile], discard_pile: List[Tile], allowed_discards: List[Tile]) -> bool:
    to_discard = input("Choose your discard: ").lower().capitalize()
    discard_tile = tile_from_str(to_discard)
    if discard_tile is None:
        return False

    for i, tile in enumerate(hand):
        if tile == discard_tile and tile in allowed_discards:
            hand.remove(tile)
            discard_pile.append(tile)
            return True
    return False


