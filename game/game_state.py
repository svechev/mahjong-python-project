from game.tiles import Suit, Tile, all_copies, tile_from_str, winds, remove_red_fives, add_red_fives, get_next_wind
from random import shuffle
from typing import List
from random import choice
from game.winning_hand_checker import get_yakus, ready_hand

# todo we just made "check pon", do other checks, maybe realize them

turns = ["left", "me", "right", "across"]


def get_next_player(curr: str) -> str:
    return turns[(winds.index(turns) + 1) % 4]


class GameState:
    def __init__(self):
        self.running = True

        self.wall = all_copies
        for _ in range(5):
            shuffle(self.wall)

        # setting up the table
        self.open_dora, self.closed_dora = self.get_dora_indicators()
        self.unveiled_dora = 1

        self.dora_tiles_count = 1
        self.dead_wall, self.wall = self.wall[:4], self.wall[4:]

        self.left_player_hand, self.wall = self.wall[:13], self.wall[13:]
        self.across_player_hand, self.wall = self.wall[:13], self.wall[13:]
        self.right_player_hand, self.wall = self.wall[:13], self.wall[13:]
        self.left_discards, self.across_discards, self.right_discards = [], [], []

        self.hand = self.get_starting_hand()  # only for rendering
        self.next_draw = None
        self.closed_tiles = list(self.hand)  # used for logic, will include tiles that are just drawn/discarded
        self.open_combos = []
        self.kan_tiles = []
        self.open_kan_tiles = []
        self.discard_pile = []  # my discard pile

        self.draws_left = 70

        self.prevalent_wind = "East"
        self.seat_wind = choice(winds)

        # setting up needed states
        self.first_turn = True
        self.last_turn = False
        self.just_kanned = False
        self.riichi = False
        self.double_riichi = False
        self.ippatsu = False
        self.furiten_temp = False
        self.furiten = False
        self.waits = []
        self.winning_yakus = []

        # states for buttons, events will make them True, if we click skip, everything goes back to False
        self.can_chii = []  # different options for chii
        self.can_pon: Tile | bool = False
        self.can_kan: Tile | bool = False
        self.can_ron: Tile | bool = False
        self.can_tsumo: Tile | bool = False
        self.can_riichi = []  # will store the tiles that can be discarded after calling riichi
        self.must_discard = False
        self.waits_action = False
        self.claimable_tile: Tile | None = None

        self.next_player = self.prevalent_wind

        # DEBUG PURPOSES
        self.hand = [Tile(Suit.MAN, 2) for _ in range(3)]
        self.hand += [Tile(Suit.MAN, 3) for _ in range(2)]
        self.hand += [Tile(Suit.MAN, 4) for _ in range(3)]
        self.hand += [Tile(Suit.MAN, i) for i in range(5, 8)]
        self.hand += [Tile(Suit.MAN, 7) for _ in range(2)]
        self.closed_tiles = list(self.hand)
        self.wall[0] = Tile(Suit.MAN, 3)
        self.wall[1] = Tile(Suit.MAN, 7)
        self.wall[3] = Tile(Suit.MAN, 3)

    def get_dora_indicators(self) -> (List[Tile], List[Tile]):
        open_dora_tiles, closed_dora_tiles = self.wall[:5], self.wall[5:10]
        self.wall = self.wall[10:]
        return open_dora_tiles, closed_dora_tiles

    def get_starting_hand(self) -> List[Tile]:
        starting_hand = self.wall[:13]
        self.wall = self.wall[13:]
        starting_hand.sort()
        return starting_hand

    def reset_buttons(self) -> None:
        self.can_chii = []
        self.can_pon = False
        self.can_kan = False
        self.can_ron = False
        self.can_tsumo = False
        self.can_riichi = []
        self.winning_yakus = []

    def activate_buttons(self, new_tile: Tile) -> None:
        if self.seat_wind == self.next_player:
            self.check_tsumo(new_tile)
            self.check_riichi(new_tile)
            if self.draws_left > 0:
                self.check_kan(new_tile, stolen=False)
        else:
            self.check_ron(new_tile)
            if self.draws_left > 0:
                self.check_pon(new_tile)
                self.check_kan(new_tile, stolen=True)
        if get_next_wind(self.next_player) == self.seat_wind and self.draws_left > 0:  # if it's left player's turn
            self.check_chii(new_tile)

    # debug function
    def print_buttons(self):
        if self.can_kan: print(f"{self.can_kan=}")
        if self.can_ron:
            print(f"{self.can_ron=} {self.winning_yakus=}")
        if self.can_tsumo: print(f"{self.can_tsumo=}, {self.winning_yakus}")
        if self.can_riichi: print(f"{self.can_riichi=}")

    def has_buttons(self) -> bool:
        if self.can_tsumo or self.can_ron or self.can_kan or self.can_pon or self.can_chii:
            return True
        if self.seat_wind == self.next_player and self.can_riichi:
            return True

    def draw(self) -> Tile | None:
        if self.draws_left == 0:  # can't play anymore
            self.running = False
            return

        if self.just_kanned:
            tile = self.dead_wall[0]
            self.dead_wall = self.dead_wall[1:]
            self.just_kanned = False
        else:
            tile = self.wall[0]
            self.wall = self.wall[1:]
        self.draws_left -= 1
        if self.draws_left == 0:
            self.last_turn = True
        return tile

    def discard_tile(self, to_discard: Tile) -> None:
        if isinstance(self.next_draw, Tile) and self.next_draw == to_discard:
            self.discard_pile.append(self.next_draw)
            waits = ready_hand(self.closed_tiles, self.kan_tiles, self.prevalent_wind, self.seat_wind, self.open_combos)
            self.waits = waits
            if self.waits: print(f"{self.waits=}")
            return
        for tile in self.hand:
            if tile == to_discard:
                self.hand.remove(tile)
                self.discard_pile.append(tile)
                self.hand.append(self.next_draw)
                self.hand.sort()
                self.closed_tiles = list(self.hand)
                waits = ready_hand(self.closed_tiles, self.kan_tiles, self.prevalent_wind, self.seat_wind,
                                   self.open_combos)
                self.waits = waits
                if self.waits: print(f"{self.waits=}")
                return

    def check_kan(self, potential_tile: Tile, stolen: bool):
        removed = remove_red_fives(self.closed_tiles)

        tile_to_check = Tile(potential_tile.suit, potential_tile.value)
        if self.closed_tiles.count(tile_to_check) == 3:
            self.can_kan = potential_tile
        if not stolen:
            for combo in self.open_combos:
                if combo.count(tile_to_check) >= 2:  # if a combo has a repeating tile, it's a triplet
                    self.can_kan = potential_tile

        add_red_fives(self.closed_tiles, removed)

    def check_pon(self, potential_tile: Tile) -> None:
        removed = remove_red_fives(self.closed_tiles)
        if self.closed_tiles.count(Tile(potential_tile.suit, potential_tile.value)) >= 2:
            self.can_pon = potential_tile
        add_red_fives(self.closed_tiles, removed)

    def check_ron(self, potential_tile: Tile) -> None:
        tile_to_check = Tile(potential_tile.suit, potential_tile.value)
        self.closed_tiles.append(tile_to_check)
        removed = remove_red_fives(self.closed_tiles)

        yakus = get_yakus(hand=self.closed_tiles,
                          kan_tiles=self.kan_tiles,
                          prev_wind=self.prevalent_wind,
                          s_wind=self.seat_wind,
                          open_combos=self.open_combos,
                          last_draw=potential_tile,
                          is_first_turn=self.first_turn,
                          is_last_turn=self.last_turn,
                          is_ron=True,
                          num_waits=len(self.waits),
                          num_kans=len(self.kan_tiles))
        self.winning_yakus = yakus
        if self.winning_yakus:
            print(f"{self.closed_tiles=}, {potential_tile=}")
            self.can_ron = potential_tile

        add_red_fives(self.closed_tiles, removed)
        self.closed_tiles.remove(tile_to_check)

    def check_tsumo(self, drawn_tile: Tile) -> None:
        tile_to_check = Tile(drawn_tile.suit, drawn_tile.value)
        self.closed_tiles.append(tile_to_check)
        removed = remove_red_fives(self.closed_tiles)
        yakus = get_yakus(hand=self.closed_tiles,
                          kan_tiles=self.kan_tiles,
                          prev_wind=self.prevalent_wind,
                          s_wind=self.seat_wind,
                          open_combos=self.open_combos,
                          last_draw=drawn_tile,
                          is_first_turn=self.first_turn,
                          is_last_turn=self.last_turn,
                          is_ron=False,
                          num_waits=len(self.waits),
                          num_kans=len(self.kan_tiles))
        self.winning_yakus = yakus
        if self.winning_yakus:
            print(f"{self.closed_tiles=}, {drawn_tile=}")
            self.can_tsumo = drawn_tile

        add_red_fives(self.closed_tiles, removed)
        self.closed_tiles.remove(tile_to_check)

    def check_chii(self, potential_tile: Tile) -> None:
        if potential_tile.is_honour():
            return

        removed = remove_red_fives(self.closed_tiles)
        tile_to_check = Tile(potential_tile.suit, potential_tile.value)  # if it was a red five we check a normal tile
        # check left
        if tile_to_check.value <= 7:
            next_tile = Tile(tile_to_check.suit, tile_to_check.value + 1)
            third_tile = Tile(tile_to_check.suit, tile_to_check.value + 2)
            if next_tile in self.closed_tiles and third_tile in self.closed_tiles:
                self.can_chii.append("left")

        # check right
        if tile_to_check.value >= 3:
            prev_tile = Tile(tile_to_check.suit, tile_to_check.value - 1)
            first_tile = Tile(tile_to_check.suit, tile_to_check.value - 2)
            if prev_tile in self.closed_tiles and first_tile in self.closed_tiles:
                self.can_chii.append("right")

        # check middle
        if 1 <= tile_to_check.value <= 8:
            prev_tile = Tile(tile_to_check.suit, tile_to_check.value - 1)
            next_tile = Tile(tile_to_check.suit, tile_to_check.value + 1)
            if prev_tile in self.closed_tiles and next_tile in self.closed_tiles:
                self.can_chii.append("middle")

        add_red_fives(self.closed_tiles, removed)

    def check_riichi(self, potential_tile: Tile) -> None:
        pass

    def clicked_ron(self) -> None:
        pass

    def clicked_tsumo(self) -> None:
        pass

    def clicked_pon(self) -> None:
        open_triplet = [self.claimable_tile]

        for tile in self.closed_tiles:
            if len(open_triplet) == 3:
                break
            if Tile(tile.suit, tile.value) == Tile(self.claimable_tile.suit, self.claimable_tile.value):
                open_triplet.append(tile)
        self.open_combos.append(open_triplet)

    def clicked_kan(self) -> None:
        pass

    def clicked_chii(self) -> None:
        pass

    def clicked_riichi(self) -> None:
        pass