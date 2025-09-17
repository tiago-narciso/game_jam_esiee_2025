import random
import pygame
from ..core import Scene
from ..config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, HEIGHT
from ..minigames import get_all_minigames
from ..utils import blit_text_center
from ..leaderboard import add_score
from .leaderboard import LeaderboardScene


class SessionScene(Scene):
    def __init__(self, game, num_games: int | None = 5, username: str | None = None):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)
        self.username = username
        # Build queue of distinct minigames based on requested count
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
        self.current_best_score = 0
        # Attempts management (shared HUD state on game)
        self.game.current_attempts_left = None

    def _push_next_if_needed(self):
        if self.index < len(self.queue) and not self.active:
            # Reset attempts for a new minigame
            self.game.current_attempts_left = self.game.max_attempts_per_game
            self.current_best_score = 0
            mg = self.queue[self.index]
            scene = mg.create_initial_scene(self.game)
            self.game.push_scene(scene)
            self.active = True

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_m):
            # abort the session and return to menu
            self.game.pop_scene()

    def update(self, dt):
        # If not currently in a minigame, push the next one
        if not self.active:
            self._push_next_if_needed()
            return
        # If the top is back to this session, then the minigame ended (popped itself)
        if self.active and self.game.top_scene() is self:
            # collect score and result for this attempt
            if self.game.last_minigame_score is not None:
                # Track best attempt score for the current minigame only
                if isinstance(self.game.last_minigame_score, (int, float)):
                    self.current_best_score = max(self.current_best_score, int(self.game.last_minigame_score))
            success = bool(self.game.last_minigame_success)
            # clear channels
            self.game.last_minigame_score = None
            self.game.last_minigame_success = None

            if success:
                # advance to next minigame
                self.scores.append(self.current_best_score)
                self.total_score += self.current_best_score
                self.index += 1
                self.active = False
            else:
                # failed attempt; decrement attempts and retry or advance
                if self.game.current_attempts_left is None:
                    self.game.current_attempts_left = self.game.max_attempts_per_game
                self.game.current_attempts_left -= 1
                if self.game.current_attempts_left <= 0:
                    # out of attempts: advance
                    self.scores.append(self.current_best_score)
                    self.total_score += self.current_best_score
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
                # session complete → leaderboard
                total = self.total_score
                highlight_name = self.username or "Anonyme"
                add_score(highlight_name, total)
                # Close session, then show leaderboard with highlight
                self.game.pop_scene()
                self.game.push_scene(LeaderboardScene(self.game, highlight_username=highlight_name, highlight_score=total))
                return
            self._push_next_if_needed()

    def draw(self, screen):
        # Simple waiting/transition screen between minigames
        screen.fill(BG_COLOR)
        title = self.title_font.render("Session de mini-jeux", True, PRIMARY_COLOR)
        blit_text_center(screen, title, 80)
        user = self.username or "—"
        attempts_left = self.game.current_attempts_left if self.game.current_attempts_left is not None else self.game.max_attempts_per_game
        status = f"Joueur: {user}  |  Jeu {min(self.index + (0 if self.active else 1), self.num_games)} / {self.num_games} — Score total: {self.total_score} — Essais restants: {attempts_left}"
        blit_text_center(screen, self.ui_font.render(status, True, PRIMARY_COLOR), 130)
        blit_text_center(screen, self.ui_font.render("Échap/M pour quitter la session", True, SECONDARY_COLOR), HEIGHT - 30)
