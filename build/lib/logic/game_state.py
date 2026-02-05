from src.logic.tile import *
from random import shuffle
from typing import List
from random import choice
from src.rules.winning_hand import *
from time import sleep

turns = ["left", "me", "right", "across"]


def get_next_player(curr: str) -> str:
    return turns[(turns.index(curr) + 1) % 4]


class GameState:
    def __init__(self) -> None:
        self.running = True
        self.round_ended = False

        self.wall = all_copies
        for _ in range(5):
            shuffle(self.wall)

        # setting up the table
        self.open_dora_indicator, self.closed_dora_indicator = self.get_dora_indicators()
        self.unveiled_dora = 1

        self.dead_wall, self.wall = self.wall[:4], self.wall[4:]

        self.left_player_hand, self.wall = self.wall[:13], self.wall[13:]
        self.across_player_hand, self.wall = self.wall[:13], self.wall[13:]
        self.right_player_hand, self.wall = self.wall[:13], self.wall[13:]
        self.left_discards, self.across_discards, self.right_discards = [], [], []

        self.hand = self.get_starting_hand()  # only for rendering
        self.next_draw: Tile | None = None
        self.closed_tiles = self.hand.copy()  # used for logic, will include tiles that are just drawn/discarded
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
        self.furiten = False
        self.waits = []
        self.winning_yakus = []
        self.extra_yakus = []
        self.winning_tile = None
        self.winning_method = None
        self.final_scores: list[tuple[int, str]] = []

        # states for buttons, events will make them True, if we click skip, everything goes back to False
        self.can_chii = []  # different options for chii
        self.can_pon: Tile | bool = False
        self.can_kan: Tile | bool = False
        self.can_ron: Tile | bool = False
        self.can_tsumo: Tile | bool = False
        self.can_riichi = False
        self.discard_for_riichi = []  # the tiles that can be discarded after calling riichi
        self.must_discard = False
        self.waits_action = False
        self.claimable_tile: Tile | None = None

        w1 = self.prevalent_wind
        w2 = get_next_wind(w1)
        w3 = get_next_wind(w2)
        w4 = get_next_wind(w3)
        if self.seat_wind == w1:
            self.next_player = "me"
        elif self.seat_wind == w2:
            self.next_player = "left"
        elif self.seat_wind == w3:
            self.next_player = "across"
        elif self.seat_wind == w4:
            self.next_player = "right"

        # DEBUG PURPOSES - great hand
        '''
        self.hand = [Tile(Suit.WIND, "East") for _ in range(2)]
        self.hand += [Tile(Suit.MAN, 3) for _ in range(2)]
        self.hand += [Tile(Suit.MAN, 4) for _ in range(3)]
        self.hand += [Tile(Suit.MAN, i) for i in range(5, 7)]
        self.hand += [Tile(Suit.MAN, 7) for _ in range(3)]
        self.hand += [Tile(Suit.MAN, 9)]
        self.hand[3] = Tile(Suit.MAN, 5, is_red_five=True)
        self.hand.sort()
        self.closed_tiles = self.hand.copy()
        self.wall[0] = Tile(Suit.MAN, 9)
        self.wall[1+4] = Tile(Suit.WIND, "East")
        self.wall[5+3] = Tile(Suit.SOU, 7)
        '''

        # DEBUG PURPOSES - kan testing
        '''
        self.hand = [Tile(Suit.SOU, 5) for _ in range(2)]
        self.hand += [Tile(Suit.SOU, 6) for _ in range(2)]
        self.hand[0] = Tile(Suit.SOU, 5, is_red_five=True)
        self.hand += [Tile(Suit.MAN, 3) for _ in range(1)]
        self.hand += [Tile(Suit.MAN, 4) for _ in range(3)]
        self.hand += [Tile(Suit.MAN, i) for i in range(5, 8)]
        self.hand += [Tile(Suit.PIN, 7) for _ in range(2)]
        self.hand[8] = Tile(Suit.MAN, 5, is_red_five=True)
        self.hand.sort()
        self.closed_tiles = self.hand.copy()
        self.wall[0] = Tile(Suit.SOU, 5)
        self.wall[1] = Tile(Suit.MAN, 7)
        self.wall[4] = Tile(Suit.SOU, 5)
        self.wall[5] = Tile(Suit.MAN, 4)
        self.dead_wall[0] = Tile(Suit.MAN, 9)
        '''

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
        self.can_riichi = False
        if not self.riichi:
            self.discard_for_riichi = []
        self.winning_yakus = []

    def activate_buttons(self, new_tile: Tile) -> None:
        if self.next_player == "me":
            self.check_tsumo(new_tile)
            if not self.riichi:
                self.check_riichi(new_tile)
            if self.draws_left > 0:
                self.check_kan(new_tile, stolen=False)
        else:  # opponent discarded a tile
            self.check_ron(new_tile)
            if not self.riichi:
                if self.draws_left > 0:
                    self.check_pon(new_tile)
                    self.check_kan(new_tile, stolen=True)
                    if self.next_player == "left":  # if it's left player's turn
                        self.check_chii(new_tile)

    def calculate_final_scores(self) -> None:
        if self.riichi:
            if self.double_riichi:
                self.winning_yakus.append("Double riichi")
            else:
                self.winning_yakus.append("Riichi")
            if self.ippatsu:
                self.winning_yakus.append("Ippatsu")

        # get yakus first
        for my_yaku in self.winning_yakus:
            han = yaku_values[my_yaku]
            if self.open_combos and my_yaku in yakus_cheaper_open_list:
                han -= 1
            self.final_scores.append((han, my_yaku))

        # then dora and red fives
        red_five_count, player_dora_count = 0, 0

        closed_kan_tiles = []
        for tile in self.kan_tiles:
            if tile.value != 5:
                for _ in range(4):
                    closed_kan_tiles.append(tile)
            else:
                for _ in range(3):
                    closed_kan_tiles.append(tile)
                closed_kan_tiles.append(Tile(tile.suit, tile.value, is_red_five=True))

        open_tiles = [tile for combo in self.open_combos for tile in combo]

        player_tiles = [*self.closed_tiles, *open_tiles, *closed_kan_tiles, self.winning_tile]

        dora_tiles = [tile.dora() for tile in self.open_dora_indicator[:self.unveiled_dora]]
        for tile in player_tiles:
            player_dora_count += dora_tiles.count(Tile(tile.suit, tile.value))
            if tile.red_five:
                red_five_count += 1

        if player_dora_count:
            self.final_scores.append((player_dora_count, "Dora"))
        if red_five_count:
            self.final_scores.append((red_five_count, "Red five"))

        if self.riichi:
            player_hidden_dora_count = 0
            closed_dora_tiles = [tile.dora() for tile in self.closed_dora_indicator[:self.unveiled_dora]]
            for tile in player_tiles:
                player_hidden_dora_count += closed_dora_tiles.count(Tile(tile.suit, tile.value))
            if player_hidden_dora_count:
                self.final_scores.append((player_hidden_dora_count, "Ura Dora"))

    def has_buttons(self) -> bool:
        if self.can_tsumo or self.can_ron or self.can_kan or self.can_pon or self.can_chii:
            return True
        if self.next_player == "me" and self.can_riichi:
            return True
        return False

    def draw(self) -> Tile | None:
        sleep(0.5)
        if self.draws_left == 0:  # can't play anymore
            self.round_ended = True
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

        else:
            for tile in self.hand:
                if tile == to_discard:
                    remove_tile_from_hand(self.hand, tile)
                    self.discard_pile.append(tile)
                    if self.next_draw is not None:
                        add_tile_to_hand(self.hand, self.next_draw)
                    self.closed_tiles = list(self.hand)
                    waits = ready_hand(self.closed_tiles, self.kan_tiles, self.prevalent_wind, self.seat_wind,
                                       self.open_combos)
                    self.waits = waits
                    break

        self.next_draw = None
        self.must_discard = False
        self.claimable_tile = None
        self.waits_action = False
        self.next_player = get_next_player(self.next_player)
        if self.first_turn:
            self.first_turn = False

        # cancel ippatsu when discarding (except when we just called riichi)
        if not self.discard_for_riichi and self.ippatsu:
            self.ippatsu = False
        self.discard_for_riichi = []

        if self.just_kanned:
            self.just_kanned = False

        if not self.riichi:
            self.furiten = False

    def pop_discard_pile(self) -> None:
        if self.next_player == "left":
            self.left_discards.pop()
        elif self.next_player == "across":
            self.across_discards.pop()
        elif self.next_player == "right":
            self.right_discards.pop()

    def check_kan(self, potential_tile: Tile, stolen: bool) -> None:
        removed = remove_red_fives(self.closed_tiles)

        tile_to_check = Tile(potential_tile.suit, potential_tile.value)
        if stolen and not self.riichi and self.closed_tiles.count(tile_to_check) == 3:
            self.can_kan = potential_tile
        if not stolen:
            add_tile_to_hand(self.closed_tiles, tile_to_check)

            # check for open kan
            if not self.riichi:
                for combo in self.open_combos:
                    # if a combo has a repeating tile, it's a triplet; and if that tile is in our hand, we can kan
                    if combo[0] == combo[1] and combo[0] in self.closed_tiles:
                        self.can_kan = potential_tile

            # check for closed kan
            quad_tiles = [tile for tile in self.closed_tiles if self.closed_tiles.count(tile) == 4]
            if quad_tiles:
                self.can_kan = quad_tiles[0]

            remove_tile_from_hand(self.closed_tiles, tile_to_check)

        add_red_fives(self.closed_tiles, removed)

    def check_pon(self, potential_tile: Tile) -> None:
        removed = remove_red_fives(self.closed_tiles)
        if self.closed_tiles.count(Tile(potential_tile.suit, potential_tile.value)) >= 2:
            self.can_pon = potential_tile
        add_red_fives(self.closed_tiles, removed)

    def check_ron(self, potential_tile: Tile) -> None:
        if self.furiten:
            return

        add_tile_to_hand(self.closed_tiles, potential_tile)

        is_ron = False if self.riichi else True
        yakus = get_yakus(hand=self.closed_tiles,
                          kan_tiles=self.kan_tiles,
                          prev_wind=self.prevalent_wind,
                          s_wind=self.seat_wind,
                          open_combos=self.open_combos,
                          last_draw=potential_tile,
                          is_first_turn=self.first_turn,
                          is_last_turn=self.last_turn,
                          is_ron=is_ron,
                          num_waits=len(self.waits),
                          num_kans=len(self.kan_tiles) + len(self.open_kan_tiles))

        if yakus:
            self.can_ron = potential_tile

        if self.riichi and "Tsumo" in yakus:
            yakus.remove("Tsumo")

        self.winning_yakus = yakus

        remove_tile_from_hand(self.closed_tiles, potential_tile)

    def check_tsumo(self, drawn_tile: Tile) -> None:
        add_tile_to_hand(self.closed_tiles, drawn_tile)

        yakus = get_yakus(hand=self.closed_tiles,
                          kan_tiles=self.kan_tiles,
                          prev_wind=self.prevalent_wind,
                          s_wind=self.seat_wind,
                          open_combos=self.open_combos,
                          last_draw=drawn_tile,
                          is_after_kan=self.just_kanned,
                          is_first_turn=self.first_turn,
                          is_last_turn=self.last_turn,
                          is_ron=False,
                          num_waits=len(self.waits),
                          num_kans=len(self.kan_tiles) + len(self.kan_tiles) + len(self.open_kan_tiles))
        self.winning_yakus = yakus
        if self.winning_yakus:
            self.can_tsumo = drawn_tile

        remove_tile_from_hand(self.closed_tiles, drawn_tile)

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
        if self.open_combos or self.draws_left < 4:
            return

        add_tile_to_hand(self.closed_tiles, potential_tile)
        to_discard = discard_for_ready_hand(self.closed_tiles, self.kan_tiles, self.prevalent_wind, self.seat_wind,
                                            self.open_combos)
        if to_discard:
            self.can_riichi = True
            self.discard_for_riichi = to_discard
        self.closed_tiles.remove(potential_tile)

    def clicked_ron(self) -> None:
        self.winning_tile = self.can_ron
        self.winning_method = "Ron"
        self.round_ended = True
        self.calculate_final_scores()

    def clicked_tsumo(self) -> None:
        self.winning_tile = self.can_tsumo
        self.winning_method = "Tsumo"
        self.round_ended = True
        self.calculate_final_scores()

    def clicked_pon(self) -> None:
        open_triplet = [self.claimable_tile]

        for tile in self.closed_tiles:
            if len(open_triplet) == 3:
                break
            if Tile(tile.suit, tile.value) == Tile(self.claimable_tile.suit, self.claimable_tile.value):
                open_triplet.append(tile)

        open_triplet.sort()
        self.open_combos.append(open_triplet)

        remove_tile_from_hand(self.hand, self.claimable_tile, 2)
        self.closed_tiles = self.hand.copy()

        self.pop_discard_pile()

    def clicked_kan(self, stolen: bool) -> None:
        triplet = []
        is_closed = False

        if stolen:
            to_claim = self.claimable_tile
            for _ in range(4):
                triplet.append(Tile(to_claim.suit, to_claim.value))

            remove_tile_from_hand(self.hand, to_claim, 3)
            self.pop_discard_pile()

        else:  # not stolen
            add_tile_to_hand(self.hand, self.next_draw)
            removed = remove_red_fives(self.hand)
            tile_quad = [tile for tile in self.hand if self.hand.count(tile) == 4]

            if tile_quad:  # closed kan
                is_closed = True
                for _ in range(4):
                    triplet.append(tile_quad[0])
                remove_tile_from_hand(self.hand, tile_quad[0], 4)
                self.kan_tiles.append(tile_quad[0])

            else:  # open kan
                open_triplets = [combo for combo in self.open_combos if combo[0] == combo[1]]
                for triplet in open_triplets:
                    for tile in self.hand:
                        if triplet[0] == tile:
                            add_tile_to_hand(triplet, tile)
                            remove_tile_from_hand(self.hand, triplet[0])

            add_red_fives(self.hand, removed)

        triplet.sort()
        if triplet[3].value == 5:
            if not triplet[0].red_five and not triplet[1].red_five and not triplet[2].red_five:
                triplet[3] = Tile(triplet[3].suit, 5, is_red_five=True)

        if not is_closed:
            self.open_kan_tiles.append(self.next_draw)
            if stolen:
                self.open_combos.append(triplet)

        self.closed_tiles = self.hand.copy()
        self.closed_tiles.sort()
        self.just_kanned = True
        self.next_draw = None
        self.unveiled_dora += 1

    def clicked_chii(self, option: str) -> None:
        to_claim = self.claimable_tile
        open_sequence = [to_claim]
        if option == "left":
            for tile in self.hand:
                if consecutive(to_claim, tile):
                    open_sequence.append(tile)
                    self.hand.remove(tile)
                    break

            second = to_claim.dora()
            for tile in self.hand:
                if consecutive(second, tile):
                    open_sequence.append(tile)
                    self.hand.remove(tile)
                    break

        elif option == "middle":
            for tile in self.hand:
                if consecutive(tile, to_claim):
                    open_sequence.append(tile)
                    self.hand.remove(tile)
                    break

            for tile in self.hand:
                if consecutive(to_claim, tile):
                    open_sequence.append(tile)
                    self.hand.remove(tile)
                    break

        elif option == "right":
            for tile in self.hand:
                if consecutive(tile, to_claim):
                    open_sequence.append(tile)
                    self.hand.remove(tile)
                    break

            second = Tile(to_claim.suit, to_claim.value - 1)
            for tile in self.hand:
                if consecutive(tile, second):
                    open_sequence.append(tile)
                    self.hand.remove(tile)
                    break

        self.closed_tiles = self.hand.copy()
        open_sequence.sort()
        self.open_combos.append(open_sequence)

        self.pop_discard_pile()

    def clicked_riichi(self) -> None:
        self.riichi = True
        self.ippatsu = True
        if self.first_turn:
            self.double_riichi = True

    def clicked_skip(self) -> None:
        if self.next_player != "me":
            self.waits_action = False

        # it was an opponent's discard
        if self.next_player != "me":
            self.next_player = get_next_player(self.next_player)
        else:  # skipped action on our turn
            if not self.riichi:
                self.must_discard = True
            else:
                self.waits_action = False

        if self.can_ron or (self.can_tsumo and self.riichi):
            self.furiten = True
