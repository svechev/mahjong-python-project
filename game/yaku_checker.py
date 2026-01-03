from game.tiles import Suit, Tile, split_hand
from typing import List

yaku_1han = ["All simples", "Riichi", "Ippatsu", "Prevalent wind", "Seat wind", "White dragon", "Green dragon",
             "Red dragon", "After a kan", "Under the sea", "Tsumo", "Pure double sequence", "Pinfu",
             "Under the river"]
yaku_2han = ["All triplets", "Triple triplets", "Mixed triple sequence", "Three quads", "Little three dragons",
             "Pure straight", "Seven pairs", "All terminals and honors", "Half outside hand", "Double riichi",
             "Three concealed triplets"]
yaku_3han = ["Half flush", "Twice pure double sequence", "Fully outside hand"]
yaku_4han = ["Mangan at draw"]  # special case
yaku_6han = ["Full flush"]
yakuman_list = ["Thirteen orphans", "Four quads", "Big three dragons",
                "Four little winds", "Blessing of heaven", "Nine gates", "All honors", "All green", "All terminals",
                "Four concealed triplets", "Blessing of earth"]
double_yakuman_list = ["Four big winds", "Thirteen-wait thirteen orphans", "True nine gates",
                       "Single-wait four concealed triplets"]

yakus_cheaper_open_list = ["Half flush", "Full flush", "Half outside hand", "Fully outside hand", "Pure straight",
                           "Mixed triple sequence"]


yaku_values = {}
for yaku in yaku_1han:
    yaku_values[yaku] = 1
for yaku in yaku_2han:
    yaku_values[yaku] = 2
for yaku in yaku_3han:
    yaku_values[yaku] = 3
for yaku in yaku_6han:
    yaku_values[yaku] = 6
for yaku in yakuman_list:
    yaku_values[yaku] = 13
for yaku in double_yakuman_list:
    yaku_values[yaku] = 26


def winning_combination(sequences: List[List[Tile]], triplets: List[List[Tile]], hand: List[Tile],
                        rest: List[Tile], pair: List[Tile]) -> bool:
    return len(sequences + triplets) == 4 or seven_pairs(hand, []) or thirteen_orphans(hand) or nine_gates(rest, pair)


def seven_pairs(hand: List[Tile], add_pairs: List[Tile]) -> bool:
    if len(hand) < 14:  # no kan allowed
        return False
    pairs = [hand[i] == hand[i + 1] for i in range(0, 12, 2)]
    if False not in pairs:
        for i in range(0, 12, 2):
            add_pairs.append(hand[i])  # store the pairs in the list for further use
        return True


def all_simples(hand: List[Tile], kan_tiles: List[Tile]) -> bool:
    simples = [tile for tile in [*hand, *kan_tiles] if not tile.is_honour() and not tile.is_terminal()]
    return len(simples) == len([*hand, *kan_tiles])


def all_triplets(triplets: List[List[Tile]]) -> bool:
    return len(triplets) == 4


def half_flush(hand: List[Tile], kan_tiles: List[Tile]) -> bool:
    sorted_hand = [*list(hand), *kan_tiles]
    sorted_hand.sort()
    man, pin, sou, honours = split_hand(sorted_hand)
    empty_suits = len([suit for suit in [man, pin, sou] if not suit])
    return empty_suits == 2 and honours


def full_flush(hand: List[Tile], kan_tiles: List[Tile]) -> bool:
    sorted_hand = [*list(hand), *kan_tiles]
    sorted_hand.sort()
    man, pin, sou, honours = split_hand(sorted_hand)
    empty_suits = len([suit for suit in [man, pin, sou] if not suit])
    return empty_suits == 2 and not honours


def white_dragon(triplets: List[List[Tile]]) -> bool:
    dragons = [triplet for triplet in triplets if triplet[0] == Tile(Suit.DRAGON, "White")]
    return len(dragons) > 0


def green_dragon(triplets: List[List[Tile]]) -> bool:
    dragons = [triplet for triplet in triplets if triplet[0] == Tile(Suit.DRAGON, "Green")]
    return len(dragons) > 0


def red_dragon(triplets: List[List[Tile]]) -> bool:
    dragons = [triplet for triplet in triplets if triplet[0] == Tile(Suit.DRAGON, "Red")]
    return len(dragons) > 0


def big_three_dragons(triplets: List[List[Tile]]) -> bool:
    return white_dragon(triplets) and green_dragon(triplets) and red_dragon(triplets)


def little_three_dragons(triplets: List[List[Tile]], pair: List[Tile]) -> bool:
    filtered = [combo for combo in [*triplets, pair] if combo[0].suit == Suit.DRAGON]
    return len(filtered) == 3 and pair[0].suit == Suit.DRAGON


def prevalent_wind(triplets: List[List[Tile]], prev_wind: str) -> bool:
    for triplet in triplets:
        if triplet[0].value == prev_wind:
            return True
    return False


def seat_wind(triplets: List[List[Tile]], s_wind: str) -> bool:
    for triplet in triplets:
        if triplet[0].value == s_wind:
            return True
    return False


def four_big_winds(triplets: List[List[Tile]]):
    wind_triplets = [triplet for triplet in triplets if triplet[0].suit == Suit.WIND]
    return len(wind_triplets) == 4


def all_terminals_and_honors(hand: List[Tile], kan_tiles) -> bool:
    sorted_tiles = [*list(hand), *kan_tiles]
    sorted_tiles.sort()
    filtered = [tile for tile in sorted_tiles if tile.is_honour() or tile.is_terminal()]
    honours = [tile for tile in sorted_tiles if tile.is_honour()]
    return len(filtered) == len(sorted_tiles) and 1 <= len(honours) <= len(sorted_tiles)-1


def all_terminals(hand: List[Tile]) -> bool:
    terminals = [tile for tile in hand if tile.is_terminal()]
    return len(terminals) == 14


def all_honors(hand: List[Tile]) -> bool:
    honours = [tile for tile in hand if tile.is_honour()]
    return len(honours) == 14


def half_outside_hand(sequences: List[List[Tile]], triplets: List[List[Tile]], pair: List[Tile],
                      pairs: List[Tile]) -> bool:
    if pairs:
        # special case for seven pairs
        filtered = [pair for pair in pairs if pair.is_honour() or pair.is_terminal()]
        if len(filtered) == 6:
            honours = [pair for pair in filtered if pair.is_honour()]
            return bool(honours)
        else:
            return False

    else:
        # check terminals and honors in every combo
        for combo in [*sequences, *triplets, pair]:
            filtered = [tile for tile in combo if tile.is_terminal() or tile.is_honour()]
            if not filtered:
                return False

        # check if there is at least one honor tile
        for combo in [*sequences, *triplets, pair]:
            honours = [tile for tile in combo if tile.is_honour()]
            if honours:
                return True

        return False


def fully_outside_hand(sequences: List[List[Tile]], triplets: List[List[Tile]], pair: List[Tile],
                       pairs: List[Tile]) -> bool:
    if pairs:  # special case for seven pairs
        terminals = [pair for pair in pairs if pair.is_terminal()]
        return len(terminals) == 6

    else:
        # check if there is a terminal in every combo
        for combo in [*sequences, *triplets, pair]:
            filtered = [tile for tile in combo if tile.is_terminal()]
            if not filtered:
                return False
        return True


def four_little_winds(triplets: List[List[Tile]], pair: List[Tile]) -> bool:
    filtered = [combo for combo in [*triplets, pair] if combo[0].suit == Suit.WIND]
    return len(filtered) == 4 and pair[0].suit == Suit.WIND


def pure_double_sequence(sequences: List[List[Tile]]) -> bool:
    # do 2 different sequences have the same elements?
    for i in range(len(sequences) - 1):
        same = True
        for j, elem in enumerate(sequences[i]):
            if elem != sequences[i + 1][j]:
                same = False
        if same:
            return True
    return False


def mixed_triple_sequence(sequences: List[List[Tile]]) -> bool:
    if len(sequences) < 3:
        return False

    common_sequence, count = -1, 1
    for sequence in sequences:
        if common_sequence == -1:  # set it
            common_sequence = sequence[0].value
        else:
            if sequence[0].value != common_sequence and count == 1:
                common_sequence = sequence[0].value
            else:
                count += 1

    if count < 3:
        return False

    first_tiles = [sequence[0] for sequence in sequences]
    return Tile(Suit.MAN, common_sequence) in first_tiles and Tile(Suit.PIN, common_sequence) in first_tiles and \
           Tile(Suit.SOU, common_sequence) in first_tiles


def twice_pure_double_sequence(sequences: List[List[Tile]], pairs: List[Tile]) -> bool:
    return bool(sequences) and bool(pairs)


def thirteen_orphans(hand: List[Tile]) -> bool:
    honours_terminals = [tile for tile in hand if tile.is_honour() or tile.is_terminal()]
    return len(set(honours_terminals)) >= 13


def thirteen_wait_thirteen_orphans(hand: List[Tile], last_draw: Tile, pair: List[Tile]) -> bool:
    return thirteen_orphans(hand) and last_draw == pair[0]


def triple_triplets(triplets: List[List[Tile]]) -> bool:
    if len(triplets) < 3:
        return False

    common_triplet, count = -1, 1
    for triplet in triplets:
        if common_triplet == -1:  # set it
            common_triplet = triplet[0].value
        else:
            if triplet[0].value != common_triplet and count == 1:
                common_triplet = triplet[0].value
            else:
                count += 1

    if count < 3:
        return False

    first_tiles = [triplet[0] for triplet in triplets]
    return Tile(Suit.MAN, common_triplet) in first_tiles and Tile(Suit.PIN, common_triplet) in first_tiles and \
           Tile(Suit.SOU, common_triplet) in first_tiles


def pure_straight(sequences: List[List[Tile]]) -> bool:
    if len(sequences) < 3:
        return False

    common_suit, count = None, 1
    for sequence in sequences:
        if common_suit is None:  # set it
            common_suit = sequence[0].suit
        else:
            if sequence[0].suit != common_suit and count == 1:
                common_suit = sequence[0].suit
            else:
                count += 1

    if count < 3:
        return False

    first_tiles = [sequence[0] for sequence in sequences]
    return Tile(common_suit, 1) in first_tiles and Tile(common_suit, 4) in first_tiles and \
           Tile(common_suit, 7) in first_tiles


def all_green(hand: List[Tile], kan_tiles: List[Tile]) -> bool:
    green_tiles = [Tile(Suit.SOU, i) for i in range(2, 5)]
    green_tiles.append(Tile(Suit.SOU, 6))
    green_tiles.append(Tile(Suit.SOU, 8))
    green_tiles.append(Tile(Suit.DRAGON, "Green"))

    green_in_hand = [tile for tile in [*hand, *kan_tiles] if tile in green_tiles]
    return len(green_in_hand) == len([*hand, *kan_tiles])


def pinfu(sequences: List[List[Tile]], pair: List[Tile], prev_wind: str, s_wind: str, num_waits: int) -> bool:
    if len(sequences) == 4 and num_waits == 2:
        if pair[0].suit == Suit.WIND and pair[0].value not in [prev_wind, s_wind]:
            return True
    return False


def nine_gates(rest: List[Tile], pair: List[Tile]) -> bool:
    tiles_13 = list(rest)
    tiles_13.append(pair[0])
    tiles_13.sort()
    suit = tiles_13[0].suit
    desired = [Tile(suit, 1) for _ in range(2)] + [Tile(suit, i) for i in range(1, 10)]
    desired += [Tile(suit, 9) for _ in range(2)]
    return tiles_13 == desired


def true_nine_gates(rest: List[Tile], pair: List[Tile], last_draw: Tile) -> bool:
    return nine_gates(rest, pair) and last_draw in pair



