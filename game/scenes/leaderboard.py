import pygame
from ..core import Scene
from ..config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, ACCENT_COLOR, HEIGHT, FONT_PATH
from ..utils import blit_text_center
from ..leaderboard import load_entries, LeaderboardEntry


class LeaderboardScene(Scene):
    def __init__(self, game, highlight_username: str | None = None, highlight_score: int | None = None):
        super().__init__(game)
        self.title_font = pygame.font.Font(FONT_PATH, 40)
        self.row_font = pygame.font.Font(FONT_PATH, 24)
        self.hint_font = pygame.font.Font(FONT_PATH, 20)
        self.entries = load_entries()
        self.highlight_username = highlight_username
        self.highlight_score = highlight_score

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                # back to menu
                self.game.pop_scene()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Leaderboard", True, PRIMARY_COLOR), 90)

        # Top 5
        top = self.entries[:5]
        y = 150
        for idx, e in enumerate(top, start=1):
            is_me = self.highlight_username is not None and e.username == self.highlight_username and (self.highlight_score is None or e.score == self.highlight_score)
            color = ACCENT_COLOR if is_me else PRIMARY_COLOR
            row = f"{idx:>2}. {e.username:<16} — {e.score}"
            blit_text_center(screen, self.row_font.render(row, True, color), y)
            y += 32

        # If not in top, show rank line
        if self.highlight_username is not None:
            rank = None
            for i, e in enumerate(self.entries, start=1):
                if e.username == self.highlight_username and (self.highlight_score is None or e.score == self.highlight_score):
                    rank = i
                    break
            if rank is not None and rank > 5:
                line = f"#{rank} — {self.highlight_username} — {self.highlight_score}"
                blit_text_center(screen, self.row_font.render(line, True, ACCENT_COLOR), y + 16)

        # blit_text_center(
        #     screen,
        #     self.hint_font.render("Entrée/Espace/Échap pour revenir au menu", True, SECONDARY_COLOR),
        #     HEIGHT - 40,
        # )


