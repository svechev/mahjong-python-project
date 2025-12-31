from game.round import play_round
from game.tiles import Tile

# todo make a new file: menu that has options:
# - play (after a win you can save your score/hand in a file)
# todo 2: new file "result" that has a class result - it will store the hand/kan_tiles/dora/hidden_dora/yakus/han
# - view tutorial
# - view yakus
# = view saved hands (from a file) - maybe sorted by date or han?


if __name__ == "__main__":
    yakus, han, hand, kan_tiles = play_round()
    if yakus:
        print(f"Final hand: {hand}", end=' ')
        if kan_tiles:
            print("Kan tiles: ", end=' ')
            for tile in kan_tiles:
                if tile.value == 5:
                    print([tile for _ in range(3)] + [Tile(tile.suit, 5, is_red_five=True)], end=' ')
                else:
                    print([tile for _ in range(3)], end=' ')
        print(f"\nYakus: {yakus}")
        print(f"{han} han")
    else:
        print("Not a winning hand, try again!")
