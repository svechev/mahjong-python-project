from game.tiles import print_hand, winds, Tile
from random import choice
from game.deck import Deck, discard
from game.winning_hand_checker import get_yakus, calculate_han, ready_hand, discard_for_ready_hand
from typing import List
from time import sleep

PREVALENT_WIND = "East"
seat_wind = choice(winds)

# todo try to kan a 5


def play_round() -> (List[str], int, List[Tile], List[Tile]):
    deck = Deck()
    hand = deck.get_starting_hand()
    hand.sort()

    discard_pile, kan_tiles = [], []

    first_turn = True
    after_kan = False
    just_kanned = False
    riichi = False
    double_riichi = False
    ippatsu = False

    print("Starting hand: ")
    while deck.draws_left > 0:
        print(f"\n\n\nDiscard pile: {discard_pile}")
        print("--" * 50)
        print(f"{PREVALENT_WIND} round. Seat wind: {seat_wind}")
        print(f"Draws left: {deck.draws_left-1}  Dora indicator: {deck.open_dora[:deck.dora_tiles_count]}")
        print("--" * 50)

        if just_kanned:
            draw = deck.draw(dead_wall=True)
        else:
            draw = deck.draw()

        waits = ready_hand(hand, kan_tiles, PREVALENT_WIND, seat_wind)
        if waits:
            print(f"Waits: {waits}")
        print_hand(hand, kan_tiles)
        print(f"Next draw: {draw}")
        hand.append(draw)
        hand.sort()

        # kan?
        just_kanned = False
        quads = [tile for tile in hand if hand.count(tile) == 4]
        quads += [tile5 for tile5 in hand if hand.count(tile5) == 3 and Tile(tile5.suit, 5, is_red_five=True) in hand]
        for tile in quads:
            command = input(f"Kan {tile}? (y/n): ")
            while command not in ["y", "n"]:
                command = input(f"Kan {tile}? (y/n): ")
            if command == "y":
                tile_at = hand.index(tile)
                hand = [tile for tile in hand if hand.index(tile) < tile_at or hand.index(tile) > tile_at + 3]
                kan_tiles.append(tile)
                deck.dora_tiles_count += 1
                after_kan = True
                just_kanned = True
                break
        if just_kanned:
            continue

        # riichi?
        if not riichi:
            allowed_discards = discard_for_ready_hand(hand, kan_tiles, PREVALENT_WIND, seat_wind)
            if allowed_discards:
                if first_turn:
                    print("Double", end=' ')
                command = input("Riichi? (y/n): ")
                while command not in ["y", "n"]:
                    command = input("Riichi? (y/n): ")
                if command == "y":
                    while True:
                        if discard(hand, discard_pile, allowed_discards):
                            break
                    riichi = True
                    ippatsu = True
                    if first_turn:
                        double_riichi = True
                    continue

        # reset the round at the start?
        if first_turn and len(set([tile for tile in hand if tile.is_honour() or tile.is_terminal()])) >= 9:
            command = input("Draw? (y/n): ")
            while command not in ["y", "n"]:
                command = input("Draw? (y/n): ")
            if command == "y":
                print("Restarting the round!")
                play_round()

        # win?
        yakus = get_yakus(hand, kan_tiles, PREVALENT_WIND, seat_wind, last_draw=draw, num_waits=len(waits))
        if yakus:
            command = input("Tsumo? (y/n): ")
            while command not in ["y", "n"]:
                command = input("Tsumo? (y/n): ")
            if command == "y":
                # some special yakus
                if first_turn:
                    yakus.append("Blessing of heaven")
                if deck.draws_left == 0:
                    yakus.append("Under the sea")
                if after_kan:
                    yakus.append("After a kan")
                if ippatsu:
                    yakus.append("Ippatsu")
                if riichi:
                    yakus.append("Riichi")
                if double_riichi:
                    yakus.append("Double riichi")
                    if "Riichi" in yakus:
                        yakus.remove("Riichi")

                han = calculate_han(yakus)

                # count dora
                print(f"Dora indicator: {deck.open_dora[:deck.dora_tiles_count]}")
                for dora_indicator in deck.open_dora[:deck.dora_tiles_count]:
                    dora_tile = dora_indicator.dora()
                    han += hand.count(dora_tile)


                # count hidden dora
                if riichi or double_riichi:
                    print(f"Hidden dora indicator: {deck.closed_dora[:deck.dora_tiles_count]}\n")
                    for dora_indicator in deck.closed_dora[:deck.dora_tiles_count]:
                        dora_tile = dora_indicator.dora()
                        han += hand.count(dora_tile)


                # count red fives
                red_fives = [tile for tile in hand if tile.red_five]
                han += len(red_fives)

                return yakus, han, hand, kan_tiles

        if not riichi:
            while True:
                if discard(hand, discard_pile, hand):
                    break
        else:
            hand.remove(draw)
            discard_pile.append(draw)
            print("No win, discarded.")
            ippatsu = False
            sleep(1)

        after_kan = False
        first_turn = False

    # check for mangan at draw:
    filtered_discard_pile = [tile for tile in discard_pile if tile.is_honour() or tile.is_terminal()]
    if len(filtered_discard_pile) == len(discard_pile):
        return ["Mangan at draw"], 4, hand, kan_tiles

    # no win, sorry
    return [], 0, [], []
