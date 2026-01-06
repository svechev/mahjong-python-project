from game.tiles import Tile, Suit, all_tiles, winds, get_next_wind
from game.game_state import GameState
import pygame
from typing import List, Tuple, Dict

TILE_SIZE = (48, 64)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BG_COLOR = (30, 120, 30)


class Renderer:
    def __init__(self, screen) -> None:
        self.screen = screen
        self.font = pygame.font.Font(None, 32)

        self.image_back = pygame.image.load("assets/Back.png").convert_alpha()
        self.image_back = pygame.transform.smoothscale(self.image_back, TILE_SIZE)

        self.tile_rects: List[Tuple[Tile, pygame.Rect]] = []
        self.tile_images: Dict[Tile, pygame.Surface] = {}
        self.hovered_tile = None
        self.button_rects: Dict[str, pygame.Rect] = {}
        self.restart_button_rect = pygame.Rect((SCREEN_WIDTH - 100, SCREEN_HEIGHT - 35), (100, 35))

        red_fives = []
        for suit in [Suit.MAN, Suit.PIN, Suit.SOU]:
            red_fives.append(Tile(suit, 5, is_red_five=True))

        for tile in [*all_tiles, *red_fives]:
            image_path = self.image_path_from_tile(tile)
            image = pygame.image.load(image_path).convert_alpha()
            image = pygame.transform.smoothscale(image, TILE_SIZE)
            self.tile_images[tile] = image

    @staticmethod
    def image_path_from_tile(tile: Tile) -> str:
        path = "assets/"
        match tile.suit:
            case Suit.MAN:
                path += f"Man{tile.value}"
            case Suit.PIN:
                path += f"Pin{tile.value}"
            case Suit.SOU:
                path += f"Sou{tile.value}"
            case Suit.WIND:
                if tile.value == "North":
                    path += "Pei"
                elif tile.value == "East":
                    path += "Ton"
                elif tile.value == "South":
                    path += "Nan"
                else:
                    path += "Shaa"
            case Suit.DRAGON:
                if tile.value == "White":
                    path += "Haku"
                elif tile.value == "Green":
                    path += "Hatsu"
                else:
                    path += "Chun"

        if tile.red_five:
            path += "-Dora"
        path += ".png"
        return path

    def get_tile_image(self, tile: Tile) -> pygame.Surface:
        return self.tile_images[tile]

    def tiles_drawn_count(self, tile: Tile) -> int:
        amount = 0
        for drawn_tile, _ in self.tile_rects:
            if drawn_tile.suit == tile.suit and drawn_tile.value == tile.value:
                amount += 1
        return amount

    def draw_tile(self, tile: Tile | str, location: tuple[int, int], direction: str, claimable: bool = False) -> None:
        if isinstance(tile, Tile):
            image = self.get_tile_image(tile)
        else:
            image = self.image_back

        angle = 0
        match direction:
            case "up":
                angle = 0
            case "down":
                angle = 180
            case "left":
                angle = 90
            case "right":
                angle = -90
        image = pygame.transform.rotate(image, angle)

        tile_rect = None
        if isinstance(tile, Tile):
            if direction in ["up", "down"]:
                white_bg_rect = pygame.Rect(location, TILE_SIZE)
            else:  # sideways
                white_bg_rect = pygame.Rect(location, (TILE_SIZE[1], TILE_SIZE[0]))
            pygame.draw.rect(self.screen, (255, 255, 255), white_bg_rect, border_radius=4)

            tile_rect = image.get_rect(topleft=location)
            self.tile_rects.append((tile, tile_rect))

        self.screen.blit(image, location)
        if self.hovered_tile and isinstance(tile, Tile) and Tile(tile.suit, tile.value) == self.hovered_tile:
            self.draw_tile_glow(tile_rect)
        if isinstance(tile, Tile) and claimable:
            self.draw_tile_outline(tile_rect)

    def draw_tile_outline(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(
            self.screen,
            (255, 255, 0),
            rect.inflate(4, 4),
            width=3,
            border_radius=6
        )

    def draw_tile_glow(self, rect) -> None:
        highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
        highlight.fill((255, 255, 0, 60))
        self.screen.blit(highlight, rect)

    def draw_restart_button(self) -> None:
        pygame.draw.rect(self.screen, (255, 255, 255), self.restart_button_rect)

        rest_x, rest_y = SCREEN_WIDTH - 100, SCREEN_HEIGHT - 35
        self.draw_text("Restart", (rest_x + 7, rest_y + 7), color=(0, 0, 0))

    def draw_dora_indicators(self, start_loc: tuple[int, int], tiles: list[Tile], amount: int) -> None:
        x, y = start_loc[0], start_loc[1]
        self.draw_text("Dora indicators: ", (x, y))
        i = 0
        for _ in range(amount):
            self.draw_tile(tiles[i], (x + i * TILE_SIZE[0], y + 35), "up")
            i += 1
        for _ in range(5 - amount):
            self.draw_tile("back", (x + i * TILE_SIZE[0], y + 35), "up")
            i += 1
        pass

    def draw_discard_indicator(self, tile_loc: tuple[int, int]) -> None:
        pygame.draw.circle(self.screen, (255, 0, 0), (tile_loc[0] + 22, tile_loc[1] - 10), 5)

    def draw_text(self, text: str, location: tuple[int, int], color: tuple[int, int, int] = (255, 255, 255)) -> None:
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, location)

    def draw_screen(self, state: GameState) -> None:
        self.tile_rects = []
        self.button_rects.clear()
        self.screen.fill(BG_COLOR)
        self.draw_table_info(state)
        self.draw_opponents()
        self.draw_discard_piles(state)
        self.draw_hand(state)
        self.draw_buttons(state)
        self.display_waits(state)

        if state.round_ended:
            self.draw_menu(state)

        pygame.display.flip()

    def draw_table_info(self, state: GameState) -> None:  # the middle - winds, score and the top - dora indicators
        # dora indicators:
        dora_loc = SCREEN_WIDTH - TILE_SIZE[0] * 5, 5
        self.draw_dora_indicators(dora_loc, state.open_dora_indicator, state.unveiled_dora)

        # winds:
        info_rect = pygame.Rect((450, 250), (100, 100))
        pygame.draw.rect(self.screen, (30, 120, 30), info_rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), info_rect, width=3, border_radius=8)
        if len(state.prevalent_wind) == 4:
            self.draw_text(state.prevalent_wind, (477, 260))
        else:
            self.draw_text(state.prevalent_wind, (477, 260))
        self.draw_text("round", (470, 290))
        draws_left = f"x{state.draws_left}"
        self.draw_text(draws_left, (480, 320))

        # print my wind
        next_wind = state.seat_wind
        if next_wind == state.prevalent_wind:
            self.draw_text(next_wind[0], (490, 350), (255, 0, 0))
        else:
            self.draw_text(next_wind[0], (490, 350), (0, 0, 0))

        # print right player wind
        next_wind = get_next_wind(next_wind)
        if next_wind == state.prevalent_wind:
            next_wind_render = self.font.render(next_wind[0], True, (255, 0, 0))
        else:
            next_wind_render = self.font.render(next_wind[0], True, (0, 0, 0))

        next_wind_render = pygame.transform.rotate(next_wind_render, 90)
        self.screen.blit(next_wind_render, (550, 290))

        # print across player wind
        next_wind = get_next_wind(next_wind)
        if next_wind == state.prevalent_wind:
            next_wind_render = self.font.render(next_wind[0], True, (255, 0, 0))
        else:
            next_wind_render = self.font.render(next_wind[0], True, (0, 0, 0))

        next_wind_render = pygame.transform.rotate(next_wind_render, 180)
        self.screen.blit(next_wind_render, (490, 230))

        # print left player wind
        next_wind = get_next_wind(next_wind)
        if next_wind == state.prevalent_wind:
            next_wind_render = self.font.render(next_wind[0], True, (255, 0, 0))
        else:
            next_wind_render = self.font.render(next_wind[0], True, (0, 0, 0))

        next_wind_render = pygame.transform.rotate(next_wind_render, 270)
        self.screen.blit(next_wind_render, (430, 290))

    def draw_opponents(self) -> None:  # draw opponents hands
        for i in range(13):
            self.draw_tile("back", (15, 20 + i * TILE_SIZE[0]), "right")  # left hand
            self.draw_tile("back", (SCREEN_WIDTH - 350, 20 + i * TILE_SIZE[0]), "left")  # right hand
            self.draw_tile("back", (200 + i * TILE_SIZE[0], 0), "down")  # across hand

    def draw_discard_piles(self, state: GameState) -> None:  # draws discard piles
        # discard piles sizes (store 2 rows of 9 tiles)
        pile_width = 9 * TILE_SIZE[0]
        pile_height = 2 * TILE_SIZE[1]

        turn = state.next_player

        # across
        i, row = 1, 1
        for (j, tile) in enumerate(state.across_discards):
            if j == len(state.across_discards) - 1 and state.claimable_tile is not None and turn == "across":
                self.draw_tile(tile,
                               (275 + pile_width - i * TILE_SIZE[0], 80 + pile_height - row * TILE_SIZE[1]),
                               "down", claimable=True)
            else:
                self.draw_tile(tile,
                               (275 + pile_width - i * TILE_SIZE[0], 80 + pile_height - row * TILE_SIZE[1]),
                               "down")
            i += 1
            if i > 9:
                i = 1
                row += 1

        # mine
        i, row = 0, 1
        for (j, tile) in enumerate(state.discard_pile):
            self.draw_tile(tile, (320 + (i - 1) * TILE_SIZE[0], 390 + (row - 1) * TILE_SIZE[1]), "up")
            i += 1
            if i > 8:
                i = 0
                row += 1

        # left
        i, row = 0, 1
        for (j, tile) in enumerate(state.left_discards):
            if j == len(state.left_discards) - 1 and state.claimable_tile is not None and turn == "left":
                self.draw_tile(tile, (105 - (row - 2) * TILE_SIZE[1], 100 + i * TILE_SIZE[0]), "right",
                               claimable=True)
            else:
                self.draw_tile(tile, (105 - (row - 2) * TILE_SIZE[1], 100 + i * TILE_SIZE[0]), "right")
            i += 1
            if i > 8:
                i = 0
                row += 1

        # right
        i, row = 0, 1
        for (j, tile) in enumerate(state.right_discards):
            if j == len(state.right_discards) - 1 and state.claimable_tile is not None and turn == "right":
                self.draw_tile(tile,
                               (765 + (row - 1) * TILE_SIZE[1], 100 + pile_width - (i + 1) * TILE_SIZE[0]),
                               "left", claimable=True)
            else:
                self.draw_tile(tile,
                               (765 + (row - 1) * TILE_SIZE[1], 100 + pile_width - (i + 1) * TILE_SIZE[0]),
                               "left")
            i += 1
            if i > 8:
                i = 0
                row += 1

    def draw_kan_tiles(self, kan_tiles: List[Tile], loc: tuple[int, int]) -> None:
        x, y = loc

        for tile in kan_tiles:
            i = 0
            for _ in range(2):
                self.draw_tile(tile, (x + i * TILE_SIZE[0], y), "up")
                i += 1
            if tile.value == 5:
                red_five = Tile(tile.suit, tile.value, is_red_five=True)
                self.draw_tile(red_five, (x + i * TILE_SIZE[0], y), "up")
            else:
                self.draw_tile(tile, (x + i * TILE_SIZE[0], y), "up")
            i += 1

            self.draw_tile("back", (x + i * TILE_SIZE[0], y), "up")
            x += 15 + TILE_SIZE[0] * 4

    def draw_hand(self, state: GameState, y: int = 580) -> None:  # draw my hand - closed and then open tiles
        i = 0
        # closed hand
        x = 200
        for tile in state.hand:
            tile_pos = x + i * TILE_SIZE[0], y
            if state.discard_for_riichi and Tile(tile.suit, tile.value) in state.discard_for_riichi:
                self.draw_discard_indicator(tile_pos)
            self.draw_tile(tile, tile_pos, "up")
            i += 1
        if state.next_draw:
            to_check = Tile(state.next_draw.suit, state.next_draw.value)
            tile_pos = x + i * TILE_SIZE[0] + 10, y
            if state.discard_for_riichi and to_check in state.discard_for_riichi:
                self.draw_discard_indicator(tile_pos)
            self.draw_tile(state.next_draw, tile_pos, "up")

        # open tiles
        i = 0
        x, y = x + 250, y + TILE_SIZE[1] + 10
        for combo in state.open_combos:
            for tile in combo:
                self.draw_tile(tile, (x + i * TILE_SIZE[0], y), "up")
                i += 1
            x += 15

        # kan tiles
        self.draw_kan_tiles(state.kan_tiles, (50, y))

    def draw_buttons(self, state: GameState) -> None:  # draw buttons chii, pon...
        width, height = 100, 35
        x, y = 1000, 150

        # helper
        def draw_button(action: str, color: tuple[int, int, int], top: int) -> None:
            button_rect = pygame.Rect((x, top), (width, height))
            pygame.draw.rect(self.screen, color, button_rect, border_radius=8)
            self.draw_text(action, (x + 10 - len(action), top + 5))
            self.button_rects[action] = button_rect

        # restart button
        self.draw_restart_button()

        # game action buttons
        if state.can_ron:
            draw_button("Ron", (200, 0, 0), y)
        if state.can_tsumo:
            draw_button("Tsumo", (217, 56, 110), y)
        if state.can_pon:
            draw_button("Pon", (0, 0, 200), y + height + 25)
        if state.can_kan:
            draw_button("Kan", (150, 0, 150), y + height * 2 + 35)
        if state.can_chii:
            if "left" in state.can_chii:
                draw_button("Chii (L)", (0, 200, 0), y + height * 3 + 45)
            if "middle" in state.can_chii:
                draw_button("Chii (M)", (0, 200, 0), y + height * 4 + 55)
            if "right" in state.can_chii:
                draw_button("Chii (R)", (0, 200, 0), y + height * 5 + 65)
        if state.can_riichi:
            draw_button("Riichi", (245, 174, 10), y + height + 25)
        if self.button_rects:
            draw_button("Skip", (50, 50, 50), y + height * 6 + 75)

    def display_waits(self, state: GameState) -> None:
        if not state.waits:
            return

        x, y = 1000, 520
        self.draw_text("Waits:", (x, y))
        y += 30

        printed = 0
        for i in range(min(len(state.waits), 5)):
            curr_wait = state.waits[i]
            curr_x = x + i * TILE_SIZE[0]
            tiles_left = 4 - self.tiles_drawn_count(curr_wait)
            self.draw_tile(curr_wait, (curr_x, y), "up")
            if state.furiten:
                self.draw_text(f"x{tiles_left}", (curr_x + 10, y + TILE_SIZE[1] + 2), color=(255, 0, 0))
            else:
                self.draw_text(f"x{tiles_left}", (curr_x + 10, y + TILE_SIZE[1] + 2), color=(255, 255, 255))

        if len(state.waits) > 5:
            self.draw_text("...", (x + TILE_SIZE[0] * 5 + 5, 520 + TILE_SIZE[1] + 10))

    def draw_menu(self, state: GameState) -> None:
        self.screen.fill(BG_COLOR)
        # DEBUG - MAYBE DON'T FILL THE ENTIRE SCREEN BUT CREATE DIFFERENT SIZE RECTANGLES FOR EACH CASE!!
        self.draw_restart_button()

        if not state.final_scores:  # draw
            self.draw_text("Draw! Please restart.", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

        else:  # we won
            win_method = state.winning_method
            self.draw_text(f"{win_method}", (200, 50))
            if win_method == "Ron":
                self.draw_tile(state.winning_tile, (250, 30), "up")
            self.draw_hand(state, y=100)
            self.draw_dora_indicators((100, 250), state.open_dora_indicator, state.unveiled_dora)
            if state.riichi:
                self.draw_dora_indicators((400, 250), state.closed_dora_indicator, state.unveiled_dora)

            x, y = 100, 370
            for han, yaku in state.final_scores:
                self.draw_text(f"{han}  {yaku}", (x, y))
                y += 30

            total_score = sum([score[0] for score in state.final_scores])
            self.draw_text(f"Final score: {total_score} han", (x, y + 35))
            special_text = ""
            if total_score >= 26:
                special_text = "DOUBLE YAKUMAN"
            elif total_score >= 13:
                special_text = "YAKUMAN"
            elif total_score >= 11:
                special_text = "SANBAIMAN"
            elif total_score >= 8:
                special_text = "BAIMAN"
            elif total_score >= 6:
                special_text = "HANEMAN"
            elif total_score >= 4:
                special_text = "MANGAN"

            self.draw_text(special_text, (x + 250, y + 36), (255, 55, 0))
