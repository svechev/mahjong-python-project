from game.round import Round
from game.tiles import Tile
import pygame

# todo 1 Riichi, ron, tsumo
# todo 2 try to make a screen after a win: self.has_won = True maybe and draws that screen on top of the normal one

if __name__ == "__main__":
    round = Round()
    round.run()

