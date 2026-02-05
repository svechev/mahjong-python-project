from src.logic.tile import winds, Tile
from random import choice
from src.logic.game_state import GameState, get_next_player
from src.rules.winning_hand import ready_hand
from time import sleep
import pygame
from src.game_runner.renderer import Renderer

PREVALENT_WIND = "East"
seat_wind = choice(winds)


class Round:
    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Riichi Mahjong")

        self.clock = pygame.time.Clock()
        self.state = GameState()
        self.renderer = Renderer(self.screen)

    def run(self) -> None:
        while self.state.running:
            self.handle_events()
            self.update()
            if self.state.round_ended:
                sleep(1)
            self.render()

            self.clock.tick(60)

        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state.running = False
                return

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.renderer.restart_button_rect.collidepoint(mouse_pos):
                    self.state = GameState()
                    return

            if self.state.round_ended:
                continue

            self.renderer.hovered_tile = None
            for tile, rect in self.renderer.tile_rects:
                if rect.collidepoint(mouse_pos):
                    self.renderer.hovered_tile = Tile(tile.suit, tile.value)
                    break

            if self.state.waits_action:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos

                    if not self.state.must_discard:  # must click a button
                        for action, rect in self.renderer.button_rects.items():
                            if rect.collidepoint(mouse_pos):
                                match action:
                                    case "Chii (L)":
                                        self.state.clicked_chii("left")
                                    case "Chii (M)":
                                        self.state.clicked_chii("middle")
                                    case "Chii (R)":
                                        self.state.clicked_chii("right")
                                    case "Pon":
                                        self.state.clicked_pon()
                                    case "Kan":
                                        if self.state.next_player == "me":
                                            self.state.clicked_kan(stolen=False)
                                            self.state.next_draw = None
                                        else:
                                            self.state.clicked_kan(stolen=True)
                                    case "Riichi":
                                        self.state.clicked_riichi()
                                        # must wait for a discard - but only a few tiles allowed
                                        self.state.must_discard = True
                                        self.state.reset_buttons()
                                        return
                                    case "Ron":
                                        self.state.clicked_ron()
                                    case "Tsumo":
                                        self.state.clicked_tsumo()
                                    case "Skip":
                                        self.state.clicked_skip()

                                if action != "Skip":  # inspect riichi when you add it
                                    self.state.next_player = "me"
                                    if action == "Kan":
                                        self.state.waits_action = False
                                    else:
                                        self.state.must_discard = True

                                self.state.reset_buttons()
                                self.state.claimable_tile = None

                    else:  # must discard a tile
                        if self.state.next_player == "me":
                            for tile, rect in self.renderer.tile_rects:
                                if self.state.discard_for_riichi:
                                    tile_is_allowed = Tile(tile.suit, tile.value) in self.state.discard_for_riichi
                                    if rect.collidepoint(mouse_pos) and 650 > mouse_pos[1] > 579 and tile_is_allowed:
                                        if self.state.must_discard:
                                            self.state.discard_tile(tile)
                                            break
                                else:
                                    if rect.collidepoint(mouse_pos) and 650 > mouse_pos[1] > 579:
                                        if self.state.must_discard:
                                            self.state.discard_tile(tile)
                                            break

    def update(self) -> None:  # next turn
        if self.state.round_ended:
            return

        if self.state.must_discard:
            self.state.waits_action = True

        if self.state.waits_action:
            return

        if not self.state.riichi:  # update our waits if not in riichi
            waits = ready_hand(self.state.closed_tiles, self.state.kan_tiles, self.state.prevalent_wind,
                               self.state.seat_wind,
                               self.state.open_combos,
                               is_after_kan=self.state.just_kanned,
                               is_first_turn=self.state.first_turn,
                               is_last_turn=self.state.last_turn,
                               is_ron=True,
                               num_waits=1, num_kans=len(self.state.kan_tiles) + len(self.state.open_kan_tiles))
            self.state.waits = waits
            for wait in waits:
                if wait in self.state.discard_pile:
                    self.state.furiten = True

        # my turn
        if self.state.riichi and self.state.next_draw:  # already drawn a tile during riichi
            sleep(0.5)
            self.state.discard_tile(self.state.next_draw)

        elif self.state.next_player == "me":
            self.state.next_draw = self.state.draw()
            if not self.state.next_draw:
                return
            self.state.activate_buttons(self.state.next_draw)
            if not self.state.riichi:
                self.state.waits_action = True
                if not self.state.can_kan and not self.state.can_riichi and not self.state.can_tsumo:
                    self.state.must_discard = True
            else:
                if self.state.can_kan or self.state.can_tsumo:
                    self.state.waits_action = True

        # right player
        elif self.state.next_player == "right":
            right_draw = self.state.draw()
            if not right_draw:
                return
            self.state.right_discards.append(right_draw)
            self.state.activate_buttons(right_draw)
            if self.state.has_buttons():
                self.state.claimable_tile = right_draw
                self.state.waits_action = True
            else:
                self.state.next_player = get_next_player(self.state.next_player)

        # player across
        elif self.state.next_player == "across":
            across_draw = self.state.draw()
            if not across_draw:
                return
            self.state.across_discards.append(across_draw)
            self.state.activate_buttons(across_draw)
            if self.state.has_buttons():
                self.state.claimable_tile = across_draw
                self.state.waits_action = True
            else:
                self.state.next_player = get_next_player(self.state.next_player)

        # left player
        else:
            left_draw = self.state.draw()
            if not left_draw:
                return
            self.state.left_discards.append(left_draw)
            self.state.activate_buttons(left_draw)
            if self.state.has_buttons():
                self.state.claimable_tile = left_draw
                self.state.waits_action = True
            else:
                self.state.next_player = get_next_player(self.state.next_player)

    def render(self) -> None:
        self.renderer.draw_screen(self.state)
