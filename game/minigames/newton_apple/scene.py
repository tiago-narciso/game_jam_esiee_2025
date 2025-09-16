import pygame
from ...core import Scene
from ...config import WIDTH, HEIGHT, ACCENT, WHITE, DARK, GOOD, BAD, GRAY
from ...utils import blit_text_center, load_sound, render_not_center_message


class NewtonAppleScene(Scene):
    TOLERANCE = 5
    FALL_SPEED = 150

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)
        self.tree_trunk_color = (139, 69, 19)
        self.tree_foliage_color = (34, 139, 34)
        self.newton_color = (70, 130, 180)
        self.apple_color = (255, 0, 0)
        self.ground_y = HEIGHT - 60
        self.tree_rect = pygame.Rect(WIDTH // 2 - 150, self.ground_y - 250, 300, 250)
        self.newton_rect = pygame.Rect(WIDTH // 2 - 20, self.ground_y - 80, 40, 80)
        self.start_y = self.tree_rect.top + 40
        self.end_y = self.newton_rect.top - 20
        self.target_y = self.start_y + (self.end_y - self.start_y) / 2
        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")
        self.snd_click = load_sound("click.wav")
        self.reset()

    def reset(self):
        self.state = "falling"
        self.apple_y = self.start_y
        self.result = None
        self.error_px = None

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif e.key == pygame.K_r and self.state == "stopped":
                self.reset()
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == "falling":
                    self.validate(); self.state = "stopped"
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "falling":
                self.validate(); self.state = "stopped"
            elif self.state == "stopped":
                score = getattr(self, "score", 0)
                self.game.complete_minigame(score)

    def update(self, dt):
        if self.state != "falling":
            return
        self.apple_y += self.FALL_SPEED * dt
        if self.apple_y >= self.end_y:
            self.apple_y = self.end_y
            self.validate(); self.state = "stopped"

    def validate(self):
        if self.snd_click: self.snd_click.play()
        self.error_px = abs(self.apple_y - self.target_y)
        if self.error_px <= self.TOLERANCE:
            self.result = "win"
            if self.snd_success: self.snd_success.play()
        else:
            self.result = "lose"
            if self.snd_fail: self.snd_fail.play()
        max_error_for_zero = (self.end_y - self.start_y) / 2
        raw = int(100 * max(0.0, 1.0 - (self.error_px / max_error_for_zero)))
        self.score = max(0, min(100, raw))

    def draw(self, screen):
        screen.fill(DARK)
        blit_text_center(screen, self.title_font.render("Arrêtez la pomme au milieu de sa chute !", True, WHITE), 60)
        hint = "ESPACE (ou clic) pour ARRÊTER • M: Menu" if self.state == "falling" else "R pour rejouer • clic pour continuer"
        blit_text_center(screen, self.ui_font.render(hint, True, GRAY), 92)
        pygame.draw.line(screen, self.tree_foliage_color, (0, self.ground_y), (WIDTH, self.ground_y), 5)
        pygame.draw.rect(screen, self.tree_trunk_color, (self.tree_rect.centerx - 20, self.tree_rect.bottom - 100, 40, 100))
        pygame.draw.circle(screen, self.tree_foliage_color, (self.tree_rect.centerx, self.tree_rect.top + 100), 100)
        pygame.draw.rect(screen, self.newton_color, self.newton_rect)
        apple_x = self.tree_rect.centerx + 30
        pygame.draw.circle(screen, self.apple_color, (apple_x, int(self.apple_y)), 15)
        pygame.draw.line(screen, ACCENT, (apple_x - 30, self.target_y), (apple_x + 30, self.target_y), 1)
        diff = abs(self.apple_y - self.target_y)
        blit_text_center(screen, self.ui_font.render(f"Décalage: {int(diff)} px (Tolérance: {self.TOLERANCE}px)", True, WHITE), HEIGHT - 28)
        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Parfait !", True, GOOD)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (≤ {self.TOLERANCE}px)", True, WHITE)
            else:
                t1 = render_not_center_message(self.title_font)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (> {self.TOLERANCE}px)", True, WHITE)
            blit_text_center(screen, t1, HEIGHT // 2 - 10)
            blit_text_center(screen, t2, HEIGHT // 2 + 26)
            blit_text_center(screen, self.ui_font.render(f"Score: {getattr(self, 'score', 0)}", True, WHITE), HEIGHT // 2 + 50)


