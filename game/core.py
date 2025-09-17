import sys
import pygame
from .config import WIDTH, HEIGHT, FPS, TITLE
from .utils import draw_80s_computer_frame, create_scanlines


class Scene:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.game_surface = pygame.Surface((WIDTH, HEIGHT))
        self.scanlines = create_scanlines(WIDTH, HEIGHT)
        self.clock = pygame.time.Clock()

        try:
            pygame.mixer.init()
        except Exception:
            pass

        self.scenes = []
        self.running = True
        # Minigame result channel: set by minigames before they pop themselves
        self.last_minigame_score = None
        self.last_minigame_success = None
        # Attempts HUD shared state (read-only for minigames)
        self.max_attempts_per_game = 3
        self.current_attempts_left = None

    def push_scene(self, scene):
        self.scenes.append(scene)

    def pop_scene(self):
        if self.scenes:
            self.scenes.pop()

    def top_scene(self):
        return self.scenes[-1] if self.scenes else None

    def quit(self):
        self.running = False

    def complete_minigame(self, score: int, success: bool):
        """Called by a minigame when it ends to submit a score and close itself."""
        self.last_minigame_score = score
        self.last_minigame_success = success
        self.pop_scene()

    def run(self):
        while self.running and self.top_scene() is not None:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                else:
                    scene = self.top_scene()
                    if scene:
                        scene.handle_event(event)
            scene = self.top_scene()
            if scene:
                scene.update(dt)
                scene.draw(self.game_surface)
            
            # Add scanlines effect and computer frame to the game surface
            self.game_surface.blit(self.scanlines, (0, 0))
            draw_80s_computer_frame(self.game_surface)

            # Scale the final game surface to the screen size and blit it
            scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_rect().size)
            self.screen.blit(scaled_surface, (0, 0))

            pygame.display.flip()
        pygame.quit()
        sys.exit(0)
