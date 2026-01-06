from game.round import Round
from game.tiles import Tile
import pygame

# todo 1 Riichi, ron, tsumo
# todo 2 try to make a screen after a win: self.have_won = True maybe and draws that screen on top of the normal one
# todo 3 for the riichi: rejecting kan during riichi breaks - look at the update() function (or
#  add special condition after skipping), test different scenarios: ron, tsumo
#  and fix visualization - i think that's ok now though?

if __name__ == "__main__":
    round = Round()
    round.run()

