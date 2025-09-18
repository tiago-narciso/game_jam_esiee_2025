import pygame
from ..core import Scene
from ..config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, ACCENT_COLOR, HEIGHT, FONT_PATH
from ..utils import blit_text_center, load_image, scale_mouse_to_game_surface


class UsernameScene(Scene):
    def __init__(self, game, on_submit):
        super().__init__(game)
        self.on_submit = on_submit
        self.title_font = pygame.font.Font(FONT_PATH, 40)
        self.ui_font = pygame.font.Font(FONT_PATH, 24)
        self.input_font = pygame.font.Font(FONT_PATH, 32)
        self.username = ""
        self.max_len = 16

        self.trophy_img = load_image("assets/images/trophy.png", max_w=40, max_h=40)
        self.trophy_rect = self.trophy_img.get_rect(topright=(900, 20))

        self.close_img = load_image("assets/images/croix.png", max_w=40, max_h=40)
        self.close_rect = self.close_img.get_rect(topleft=(20, 20))

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            # Scale mouse coordinates to match the game surface resolution
            screen_rect = self.game.screen.get_rect()
            scaled_pos = scale_mouse_to_game_surface(e.pos, screen_rect)
            
            if self.trophy_rect.collidepoint(scaled_pos):
                from .leaderboard import LeaderboardScene
                self.game.push_scene(LeaderboardScene(self.game))
            elif self.close_rect.collidepoint(scaled_pos):
                self.game.quit()
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.game.quit()
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
                if ch.isalnum():
                    self.username += ch

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Entrer un pseudo", True, PRIMARY_COLOR), 120)
        hint = "Entrée pour valider, Échap pour annuler"
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), 160)

        display = self.username if self.username else "..."
        text = self.input_font.render(display, True, ACCENT_COLOR if self.username else SECONDARY_COLOR)
        blit_text_center(screen, text, 220)

        screen.blit(self.trophy_img, self.trophy_rect)
        screen.blit(self.close_img, self.close_rect)
