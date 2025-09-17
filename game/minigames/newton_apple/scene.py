import pygame
from ...core import Scene
from ...config import WIDTH, HEIGHT, ACCENT_COLOR, PRIMARY_COLOR, BG_COLOR, GOOD_COLOR, BAD_COLOR, SECONDARY_COLOR, FONT_PATH
from ...utils import blit_text_center, load_sound, render_not_center_message, load_image, draw_attempts


class NewtonAppleScene(Scene):
    TOLERANCE = 2
    FALL_SPEED = 150

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(FONT_PATH, 40)
        self.ui_font = pygame.font.Font(FONT_PATH, 22)
        self.tree_trunk_color = (139, 69, 19)
        self.tree_foliage_color = (34, 139, 34)
        self.newton_color = (70, 130, 180)
        self.apple_color = (255, 0, 0)
        self.ground_y = HEIGHT - 50
        
        self.tree_img = load_image("assets/images/tree.png", max_w=400, max_h=500)
        self.tree_rect = self.tree_img.get_rect(midbottom=(WIDTH // 2, self.ground_y))

        self.newton_img = load_image("assets/images/newton.png", max_w=100, max_h=100)
        self.newton_rect = self.newton_img.get_rect(midbottom=(self.tree_rect.centerx + 30, self.ground_y))

        self.apple_img = load_image("assets/images/apple.png", max_w=30, max_h=30)
        self.apple_rect = self.apple_img.get_rect()

        self.start_y = self.tree_rect.top + 45
        self.end_y = self.newton_rect.top + 10
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
                elif self.state == "stopped":
                    score = getattr(self, "score", 0)
                    success = (self.result == "win")
                    self.game.complete_minigame(score, success)
            elif self.state == "stopped":
                score = getattr(self, "score", 0)
                success = (self.result == "win")
                self.game.complete_minigame(score, success)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "falling":
                self.validate(); self.state = "stopped"
            elif self.state == "stopped":
                score = getattr(self, "score", 0)
                self.game.complete_minigame(score, self.result == "win")

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
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Arrêtez la pomme au milieu de sa chute !", True, PRIMARY_COLOR), 60)
        hint = "ESPACE (ou clic) pour ARRÊTER • M: Menu" if self.state == "falling" else "ESPACE/clic pour continuer • R pour rejouer"
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), 92)
        draw_attempts(screen, self.game, pos=(None, 26))
        
        # Draw ground behind other objects
        pygame.draw.rect(screen, self.tree_foliage_color, (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))

        screen.blit(self.tree_img, self.tree_rect)
        screen.blit(self.newton_img, self.newton_rect)

        apple_x = self.tree_rect.centerx + 30
        self.apple_rect.center = (apple_x, int(self.apple_y))
        screen.blit(self.apple_img, self.apple_rect)
        
        diff = abs(self.apple_y - self.target_y)
        blit_text_center(screen, self.ui_font.render(f"Décalage: {int(diff)} px (Tolérance: {self.TOLERANCE}px)", True, PRIMARY_COLOR), HEIGHT - 28)
        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Parfait !", True, GOOD_COLOR)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (≤ {self.TOLERANCE}px)", True, PRIMARY_COLOR)
            else:
                t1 = render_not_center_message(self.title_font)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (> {self.TOLERANCE}px)", True, PRIMARY_COLOR)
            blit_text_center(screen, t1, HEIGHT // 2 - 10)
            blit_text_center(screen, t2, HEIGHT // 2 + 26)
            blit_text_center(screen, self.ui_font.render(f"Score: {getattr(self, 'score', 0)}", True, PRIMARY_COLOR), HEIGHT // 2 + 50)
