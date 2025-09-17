import pygame
from ..core import Scene
from ..config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, ACCENT_COLOR, HEIGHT, WIDTH
from ..utils import blit_text_center, load_sound, draw_pixel_button


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.items = []  # placeholders, real callbacks wired in main factory
        self.idx = 0
        self.title_font = pygame.font.SysFont(None, 48, bold=True)
        self.item_font = pygame.font.SysFont(None, 32)
        self.hint_font = pygame.font.SysFont(None, 20)

        self.snd_move = load_sound("click.wav")

    def set_menu_items(self, items):
        self.items = items

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.game.quit()
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.idx = (self.idx - 1) % len(self.items)
                if self.snd_move:
                    self.snd_move.play()
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.idx = (self.idx + 1) % len(self.items)
                if self.snd_move:
                    self.snd_move.play()
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                _, fn = self.items[self.idx]
                fn()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Menu", True, PRIMARY_COLOR), 120)
        
        button_width = 300
        button_height = 50
        start_y = 220
        gap = 15

        for i, (label, _) in enumerate(self.items):
            rect = pygame.Rect((WIDTH - button_width) // 2, start_y + i * (button_height + gap), button_width, button_height)
            draw_pixel_button(screen, rect, label, self.item_font, selected=(i == self.idx))

        blit_text_center(
            screen,
            self.hint_font.render(
                "↑/↓ pour naviguer • Entrée pour valider • Échap pour quitter",
                True,
                SECONDARY_COLOR,
            ),
            HEIGHT - 40,
        )
