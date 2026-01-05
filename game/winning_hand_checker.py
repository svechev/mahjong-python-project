from game.tiles import all_tiles, dragon_tiles, wind_tiles
from game.tiles import add_red_fives, remove_red_fives
from collections import Counter
from game.yaku_checker import *


def calculate_han(yakus: List[str]) -> int:
    han = 0
    for curr_yaku in yakus:
        han += yaku_values[curr_yaku]
    return han


def get_sequences(suit: Suit, count: Counter, sequences: List[List[Tile]]):
    for tile_1 in [Tile(suit, i) for i in range(1, 8)]:  # last possible start tile is 7
        tile_2 = tile_1.dora()
        tile_3 = tile_2.dora()
        while count[tile_1] > 0 and count[tile_2] > 0 and count[tile_3] > 0:
            sequences.append([tile_1, tile_2, tile_3])
            count[tile_1] -= 1
            count[tile_2] -= 1
            count[tile_3] -= 1


def get_triplets(suit: Suit, count: Counter, triplets: List[List[Tile]]):
    if suit in [Suit.DRAGON, Suit.WIND]:
        possible_tiles = [tile for tile in [*dragon_tiles, *wind_tiles]]
    else:
        possible_tiles = [Tile(suit, i) for i in range(1, 10)]

    for tile in possible_tiles:
        if count[tile] >= 3:
            triplets.append([tile, tile, tile])
            count[tile] -= 3


def get_combos(rest: List[Tile], sequences_first: bool) -> (List[Tile], List[Tile]):
    man, pin, sou, honours = split_hand(rest)
    sequences, triplets = [], []
    for suit_tiles in [man, pin, sou]:
        if not suit_tiles:
            continue
        else:
            suit = suit_tiles[0].suit
        count = Counter(suit_tiles)
        if sequences_first:
            get_sequences(suit, count, sequences)
            get_triplets(suit, count, triplets)
        else:
            get_triplets(suit, count, triplets)
            get_sequences(suit, count, sequences)

    count_honours = Counter(honours)
    get_triplets(Suit.WIND, count_honours, triplets)

    return sequences, triplets


def get_yakus(hand: List[Tile], kan_tiles: List[Tile], prev_wind: str, s_wind: str,
              open_combos: List[List[Tile]], last_draw: Tile,
              is_after_kan: bool = False,
              is_first_turn: bool = False,
              is_last_turn: bool = False,
              is_ron: bool = False,
              num_waits: int = 1, num_kans: int = 1) -> (List[str]):

    removed = remove_red_fives(hand)

    open_tiles = []
    for combo in open_combos:
        open_tiles += combo

    # split the sequences and triplets - easier checks for concealed triplets
    open_triplets, open_sequences = [], []
    for combo in open_combos:
        if combo[0] == combo[1]:  # triplet
            open_triplets.append(combo)
        else:                     # sequence
            open_sequences.append(combo)

    yakus, han = [], 0
    for sequences_first in [True, False]:
        for i in range(len(hand)-1):
            curr_yakus, curr_han = [], 0

            pair, rest = [], []
            if hand[i] == hand[i + 1]:
                pair = [hand[i], hand[i + 1]]
                rest = hand[:i] + hand[i + 2:]
            if not pair:
                continue

            sequences, triplets = get_combos(rest, sequences_first=sequences_first)
            sequences += open_sequences
            triplets += open_triplets
            for tile in kan_tiles:
                triplets.append([tile for _ in range(3)])

            # check if it's a winning hand
            if winning_combination(sequences, triplets, hand, rest, pair):
                if not open_combos and not is_ron:
                    curr_yakus.append("Tsumo")  # means "fully concealed hand (and got the last tile by drawing it)"

                # print(f"this is a winning combination: {hand=}, {open_combos=}")
                # print(f"{triplets=}, {sequences=}, {pair=}")

                # winning combination means the hand has 4 triplets/sequences and a pair, now we check all the yakus
                pairs = []
                if seven_pairs(hand, pairs):
                    curr_yakus.append("Seven pairs")

                # normal yakus:
                if all_simples(hand, kan_tiles, open_tiles):
                    curr_yakus.append("All simples")
                if all_triplets(triplets):
                    curr_yakus.append("All triplets")
                if half_flush(hand, kan_tiles, open_tiles):
                    curr_yakus.append("Half flush")
                if full_flush(hand, kan_tiles, open_tiles):
                    curr_yakus.append("Full flush")
                if white_dragon(triplets):
                    curr_yakus.append("White dragon")
                if green_dragon(triplets):
                    curr_yakus.append("Green dragon")
                if red_dragon(triplets):
                    curr_yakus.append("Red dragon")
                if big_three_dragons(triplets):
                    curr_yakus.append("Big three dragons")
                if little_three_dragons(triplets, pair):
                    curr_yakus.append("Little three dragons")
                if seat_wind(triplets, s_wind):
                    curr_yakus.append("Seat wind")
                if prevalent_wind(triplets, prev_wind):
                    curr_yakus.append("Prevalent wind")
                if four_big_winds(triplets):
                    curr_yakus.append("Four big winds")
                if all_terminals_and_honors(hand, kan_tiles, open_tiles):
                    curr_yakus.append("All terminals and honors")
                if all_terminals(hand, kan_tiles, open_tiles):
                    curr_yakus.append("All terminals")
                if all_honors(hand, kan_tiles, open_tiles):
                    curr_yakus.append("All honors")
                if half_outside_hand(sequences, triplets, pair, pairs):
                    curr_yakus.append("Half outside hand")
                if fully_outside_hand(sequences, triplets, pair, pairs):
                    curr_yakus.append("Fully outside hand")
                if four_little_winds(triplets, pair):
                    curr_yakus.append("Four little winds")
                if pure_double_sequence(sequences):
                    curr_yakus.append("Pure double sequence")
                if mixed_triple_sequence(sequences):
                    curr_yakus.append("Mixed triple sequence")
                if twice_pure_double_sequence(sequences, pairs):
                    curr_yakus.append("Twice pure double sequence")
                    if "Seven pairs" in curr_yakus:
                        curr_yakus.remove("Seven pairs")
                    if "Pure double sequence" in curr_yakus:
                        curr_yakus.remove("Pure double sequence")
                if thirteen_orphans(hand):
                    curr_yakus.append("Thirteen orphans")
                    if "All terminals and honors" in curr_yakus:
                        curr_yakus.remove("All terminals and honors")
                    if "Half outside hand" in curr_yakus:
                        curr_yakus.remove("Half outside hand")
                if thirteen_wait_thirteen_orphans(hand, last_draw, pair):
                    curr_yakus.append("Thirteen-wait thirteen orphans")
                    if "Thirteen orphans" in curr_yakus:
                        curr_yakus.remove("Thirteen orphans")
                if triple_triplets(triplets):
                    curr_yakus.append("Triple triplets")
                if pure_straight(sequences):
                    curr_yakus.append("Pure straight")
                if all_green(hand, kan_tiles, open_tiles):
                    curr_yakus.append("All green")
                if len(kan_tiles) == 3:
                    curr_yakus.append("Three quads")
                if len(kan_tiles) == 4:
                    curr_yakus.append("Four quads")
                if pinfu(sequences, pair, prev_wind, s_wind, num_waits) and open_sequences == []:
                    curr_yakus.append("Pinfu")
                if nine_gates(rest, pair):
                    curr_yakus.append("Nine gates")
                    if "Full flush" in curr_yakus:
                        curr_yakus.remove("Full flush")
                    if "Pure straight" in curr_yakus:
                        curr_yakus.remove("Pure straight")
                if true_nine_gates(rest, pair, last_draw):
                    curr_yakus.append("True nine gates")
                    if "Nine gates" in curr_yakus:
                        curr_yakus.remove("Nine gates")

                # some special yakus, that are dependant on conditions outside the hand itself:
                if is_after_kan and not is_ron:
                    curr_yakus.append("After a kan")

                if is_first_turn and not open_combos and not is_ron:
                    if s_wind == prev_wind:
                        curr_yakus.append("Blessing of heaven")
                    else:
                        curr_yakus.append("Blessing of earth")
                if is_last_turn:
                    if is_ron:
                        curr_yakus.append("Under the river")
                    else:
                        curr_yakus.append("Under the sea")
                if num_kans == 3:
                    curr_yakus.append("Three quads")
                if num_kans == 4:
                    curr_yakus.append("Four quads")

                concealed_triplets = [triplet[0] for triplet in triplets if triplet not in open_triplets]
                concealed_triplets_count = len(concealed_triplets)
                if last_draw in concealed_triplets and is_ron:
                    concealed_triplets_count -= 1

                if concealed_triplets_count == 3:
                    curr_yakus.append("Three concealed triplets")
                if concealed_triplets_count == 4:
                    if num_waits == 2:
                        curr_yakus.append("Four concealed triplets")
                    else:
                        curr_yakus.append("Single-wait four concealed triplets")

                curr_han = calculate_han(curr_yakus)
                if curr_han > han:
                    han = curr_han
                    yakus = curr_yakus

    add_red_fives(hand, removed)
    # if yakus:
        # print(f"{hand=}, {open_combos=}, {yakus=}")
    return yakus


def ready_hand(hand: List[Tile], kan_tiles: List[Tile], prev_wind: str, s_wind: str,
               open_combos: List[List[Tile]]) -> List[Tile]:
    waits = []
    for tile in all_tiles:
        hand.append(tile)
        hand.sort()
        if get_yakus(hand, kan_tiles, prev_wind, s_wind, open_combos, last_draw=tile):
            waits.append(tile)
        hand.remove(tile)
    waits.sort()
    return waits


def discard_for_ready_hand(hand: List[Tile], kan_tiles: List[Tile], prev_wind: str, s_wind: str,
                           open_combos: List[List[Tile]]) -> List[Tile]:
    to_discard = []
    for tile in hand:
        hand.remove(tile)
        if ready_hand(hand, kan_tiles, prev_wind, s_wind, open_combos):
            to_discard.append(tile)
        hand.append(tile)
        hand.sort()
    to_discard = list(set(to_discard))
    to_discard.sort()
    return to_discard