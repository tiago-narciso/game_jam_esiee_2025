import pygame
from ..core import Scene
from ..config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, ACCENT_COLOR, HEIGHT, FONT_PATH
from ..utils import blit_text_center


class UsernameScene(Scene):
    def __init__(self, game, on_submit):
        super().__init__(game)
        self.on_submit = on_submit
        self.title_font = pygame.font.Font(FONT_PATH, 40)
        self.ui_font = pygame.font.Font(FONT_PATH, 24)
        self.input_font = pygame.font.Font(FONT_PATH, 32)
        self.username = ""
        self.max_len = 16
        self.allowed_extra = set("-_ ")

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                # back to previous scene (menu)
                self.game.pop_scene()
            elif e.key == pygame.K_RETURN:
                name = self.username.strip()
                if name:
                    self.on_submit(name)
                    # this scene will usually be popped by submitter
            elif e.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            else:
                ch = e.unicode
                if not ch:
                    return
                if len(self.username) >= self.max_len:
                    return
                if ch.isalnum() or ch in self.allowed_extra:
                    self.username += ch

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Entrer un pseudo", True, PRIMARY_COLOR), 120)
        hint = "Lettres/chiffres/-,_ (max 16). Entrée pour valider, Échap pour annuler"
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), 160)

        display = self.username if self.username else "—"
        text = self.input_font.render(display, True, ACCENT_COLOR if self.username else SECONDARY_COLOR)
        blit_text_center(screen, text, 220)


