import math
import pygame
from ..core import Scene
from ..config import PRIMARY_COLOR, BG_COLOR, ACCENT_COLOR, GOOD_COLOR, BAD_COLOR, SECONDARY_COLOR, WIDTH, HEIGHT
from ..utils import blit_text_center, load_sound, render_not_center_message, draw_attempts


class CenterWordScene(Scene):
    WORD = "HISTOIRE"
    TOLERANCE = 8
    BASE_SPEED = 320
    PADDING = 40

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.word_font = pygame.font.SysFont(None, 160, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)

        self.word_surf = self.word_font.render(self.WORD, True, PRIMARY_COLOR)
        self.word_rect = self.word_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.true_center_x = self.word_rect.centerx
        # Instead of an external line, we'll fill the text from left to right

        self.min_x = 0.0
        self.max_x = 1.0  # normalized fill 0..1

        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")
        self.snd_click = load_sound("click.wav")

        self.reset()

    def reset(self):
        self.state = "moving"
        self.cursor_x = self.min_x
        self.dir = +1
        self.result = None
        self.error_px = None
        self.time_acc = 0.0

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif e.key == pygame.K_r and self.state == "stopped":
                self.reset()
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == "moving":
                    self.validate()
                    self.state = "stopped"
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "moving":
                self.validate()
                self.state = "stopped"
            elif self.state == "stopped":
                # On click after finish, report score and leave
                self.game.complete_minigame(getattr(self, "score", 0), self.result == "win")

    def update(self, dt):
        if self.state != "moving":
            return
        self.time_acc += dt
        speed = self.BASE_SPEED * (1.0 + 0.10 * math.sin(self.time_acc * 4.0))
        # Convert px/s to normalized per second using word width
        word_w = self.word_rect.width if self.word_rect.width > 0 else 1
        self.cursor_x += self.dir * (speed / word_w) * dt
        if self.cursor_x >= self.max_x:
            self.cursor_x = self.max_x
            self.dir = -1
        elif self.cursor_x <= self.min_x:
            self.cursor_x = self.min_x
            self.dir = +1

    def validate(self):
        if self.snd_click:
            self.snd_click.play()
        # Evaluate error relative to 50% fill
        self.error_px = abs(self.cursor_x - 0.5) * self.word_rect.width
        if abs(self.cursor_x - 0.5) * self.word_rect.width <= self.TOLERANCE:
            self.result = "win"
            if self.snd_success:
                self.snd_success.play()
        else:
            self.result = "lose"
            if self.snd_fail:
                self.snd_fail.play()
        # Compute score: 100 max, linearly reduced by error, clamped to [0, 100]
        # 0 error -> 100, error == word width/2 -> 0
        max_error_for_zero = self.word_rect.width / 2
        raw = int(100 * max(0.0, 1.0 - (self.error_px / max_error_for_zero)))
        self.score = max(0, min(100, raw))

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Arrête la barre au centre du mot", True, PRIMARY_COLOR), 60)
        hint = (
            "ESPACE (ou clic) pour ARRÊTER • M: Menu"
            if self.state == "moving"
            else "R pour rejouer • M: Menu"
        )
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), 92)
        draw_attempts(screen, self.game, pos=(None, 26))

        # Draw the word, with a fill mask up to cursor_x
        # Base word in desaturated color
        base_surf = self.word_font.render(self.WORD, True, (100, 110, 120))
        screen.blit(base_surf, self.word_rect.topleft)

        # Filled overlay up to fraction
        filled_color = ACCENT_COLOR if self.result is None else (GOOD_COLOR if self.result == "win" else BAD_COLOR)
        filled_surf = self.word_font.render(self.WORD, True, filled_color)
        clip_width = max(0, min(self.word_rect.width, int(self.cursor_x * self.word_rect.width)))
        if clip_width > 0:
            clip_rect = pygame.Rect(self.word_rect.left, self.word_rect.top, clip_width, self.word_rect.height)
            screen.set_clip(clip_rect)
            screen.blit(filled_surf, self.word_rect.topleft)
            screen.set_clip(None)

        diff = abs(self.cursor_x - 0.5) * self.word_rect.width
        blit_text_center(
            screen,
            self.ui_font.render(
                f"Décalage: {int(diff)} px (Tolérance: {self.TOLERANCE}px)", True, PRIMARY_COLOR
            ),
            HEIGHT - 28,
        )

        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render(
                    "Parfait ! 50% atteint.", True, GOOD_COLOR
                )
                t2 = self.ui_font.render(
                    f"Erreur: {int(self.error_px)} px (≤ {self.TOLERANCE}px)", True, PRIMARY_COLOR
                )
            else:
                t1 = render_not_center_message(self.title_font)
                t2 = self.ui_font.render(
                    f"Erreur: {int(self.error_px)} px (> {self.TOLERANCE}px)", True, PRIMARY_COLOR
                )
            t3 = self.ui_font.render(f"Score: {getattr(self, 'score', 0)}", True, PRIMARY_COLOR)
            blit_text_center(screen, t1, HEIGHT // 2 - 10)
            blit_text_center(screen, t2, HEIGHT // 2 + 26)
            blit_text_center(screen, t3, HEIGHT // 2 + 50)
            hint = self.ui_font.render("Clique pour continuer", True, SECONDARY_COLOR)
            blit_text_center(screen, hint, HEIGHT // 2 + 72)
