from game.round import Round
from game.tiles import Tile
import pygame

# todo 1 BREAKS AFTER REJECTING A RON

if __name__ == "__main__":
    round = Round()
    round.run()


    '''
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
    '''
