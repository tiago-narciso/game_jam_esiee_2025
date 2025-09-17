import pygame
from ..core import Scene
from ..config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, HEIGHT, FONT_PATH
from ..utils import blit_text_center


class EndScene(Scene):
    def __init__(self, game, total_score: int, games_count: int):
        super().__init__(game)
        self.title_font = pygame.font.Font(FONT_PATH, 48)
        self.ui_font = pygame.font.Font(FONT_PATH, 26)
        self.total_score = total_score
        self.games_count = games_count

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_m):
                # Back to menu
                self.game.pop_scene()

        elif e.type == pygame.MOUSEBUTTONDOWN:
            self.game.pop_scene()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Fin de partie", True, PRIMARY_COLOR), 120)
        blit_text_center(screen, self.ui_font.render(f"Mini-jeux joués: {self.games_count}", True, PRIMARY_COLOR), 190)
        blit_text_center(screen, self.ui_font.render(f"Score total: {self.total_score}", True, PRIMARY_COLOR), 226)
        blit_text_center(screen, self.ui_font.render("Appuyez pour revenir au menu", True, SECONDARY_COLOR), HEIGHT - 40)


