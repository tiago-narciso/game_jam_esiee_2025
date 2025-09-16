import random
import pygame
from ..core import Scene
from ..config import WHITE, GRAY, DARK, HEIGHT
from ..minigames import get_all_minigames
from ..utils import blit_text_center


class SessionScene(Scene):
    def __init__(self, game, num_games: int = 5):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)
        self.num_games = num_games
        self.queue = []
        choices = get_all_minigames()
        if choices:
            self.queue = [random.choice(choices) for _ in range(num_games)]
        self.index = 0
        self.active = False
        self.scores = []
        self._push_next_if_needed()

    def _push_next_if_needed(self):
        if self.index < len(self.queue) and not self.active:
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
            # collect score if any
            if self.game.last_minigame_score is not None:
                self.scores.append(self.game.last_minigame_score)
                self.game.last_minigame_score = None
            self.index += 1
            self.active = False
            if self.index >= len(self.queue):
                # session complete
                # In the future: submit scores to leaderboard here
                self.game.pop_scene()
                return
            self._push_next_if_needed()

    def draw(self, screen):
        # Simple waiting/transition screen between minigames
        screen.fill(DARK)
        title = self.title_font.render("Session de mini-jeux", True, WHITE)
        blit_text_center(screen, title, 80)
        status = f"Jeu {min(self.index + (0 if self.active else 1), self.num_games)} / {self.num_games} — Score total: {sum(self.scores) if self.scores else 0}"
        blit_text_center(screen, self.ui_font.render(status, True, WHITE), 130)
        blit_text_center(screen, self.ui_font.render("Échap/M pour quitter la session", True, GRAY), HEIGHT - 30)



