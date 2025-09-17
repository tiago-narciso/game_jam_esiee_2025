import random
import pygame
from ..core import Scene
from ..config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, HEIGHT
from ..minigames import get_all_minigames
from ..utils import blit_text_center


class SessionScene(Scene):
    def __init__(self, game, num_games: int = None):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)
        choices = get_all_minigames()
        random.shuffle(choices)
        if num_games is None:
            num_games = len(choices)
        self.queue = choices[: max(0, min(num_games, len(choices)))]
        self.num_games = len(self.queue)
        self.index = 0
        self.active = False
        self.scores = []
        self.total_score = 0
        # Attempts management
        self.game.current_attempts_left = None
        self._push_next_if_needed()

    def _push_next_if_needed(self):
        if self.index < len(self.queue) and not self.active:
            # Reset attempts for a new minigame
            self.game.current_attempts_left = self.game.max_attempts_per_game
            mg = self.queue[self.index]
            scene = mg.create_initial_scene(self.game)
            self.game.push_scene(scene)
            self.active = True

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_m):
            # abort the session and return to menu
            self.game.pop_scene()

    def update(self, dt):
        # If the top is back to this session, then the minigame ended (popped itself)
        if self.active and self.game.top_scene() is self:
            # collect score and result
            if self.game.last_minigame_score is not None:
                self.scores.append(self.game.last_minigame_score)
                self.total_score = sum(self.scores)
            success = bool(self.game.last_minigame_success)
            # clear channels
            self.game.last_minigame_score = None
            self.game.last_minigame_success = None

            if success:
                # advance to next minigame
                self.index += 1
                self.active = False
            else:
                # failed attempt; decrement attempts and retry or advance
                if self.game.current_attempts_left is None:
                    self.game.current_attempts_left = self.game.max_attempts_per_game
                self.game.current_attempts_left -= 1
                if self.game.current_attempts_left <= 0:
                    # out of attempts: advance
                    self.index += 1
                    self.active = False
                else:
                    # retry same minigame immediately
                    mg = self.queue[self.index]
                    scene = mg.create_initial_scene(self.game)
                    self.game.push_scene(scene)
                    # still active
                    return

            if self.index >= len(self.queue):
                # session complete → End screen
                from .end import EndScene
                self.game.push_scene(EndScene(self.game, self.total_score, self.num_games))
                # Then remove session scene underneath end when end exits back
                self.game.pop_scene()
                return
            self._push_next_if_needed()

    def draw(self, screen):
        # Simple waiting/transition screen between minigames
        screen.fill(BG_COLOR)
        title = self.title_font.render("Session de mini-jeux", True, PRIMARY_COLOR)
        blit_text_center(screen, title, 80)
        status = f"Jeu {min(self.index + (0 if self.active else 1), self.num_games)} / {self.num_games} — Score total: {self.total_score} — Essais restants: {self.game.current_attempts_left if self.game.current_attempts_left is not None else self.game.max_attempts_per_game}"
        blit_text_center(screen, self.ui_font.render(status, True, PRIMARY_COLOR), 130)
        blit_text_center(screen, self.ui_font.render("Échap/M pour quitter la session", True, SECONDARY_COLOR), HEIGHT - 30)
