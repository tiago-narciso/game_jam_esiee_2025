import random
import pygame
from ...core import Scene
from ...config import WIDTH, HEIGHT, PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, ACCENT_COLOR, GOOD_COLOR, BAD_COLOR, CELEBRITIES, LIFE_KEY_SPEED, LIFE_TIMELINE_PADDING_YEARS, LIFE_TARGET_KIND, FONT_PATH
from ...utils import blit_text_center, clamp, draw_attempts, load_sound, render_not_center_message, render_win_message


class LifeMidpointScene(Scene):
    CURSOR_SPEED = LIFE_KEY_SPEED  # pixels per second for keyboard
    TOLERANCE_YEARS = 0  # years within target for success

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(FONT_PATH, 36)
        self.title_font_small = pygame.font.Font(FONT_PATH, 34)
        self.ui_font = pygame.font.Font(FONT_PATH, 22)
        self.large_font = pygame.font.Font(FONT_PATH, 28)
        self.person = random.choice(CELEBRITIES)
        name, birth, death = self.person
        self.name = name
        self.birth = birth
        self.death = death
        self.min_year = self.birth - LIFE_TIMELINE_PADDING_YEARS
        self.max_year = self.death + LIFE_TIMELINE_PADDING_YEARS
        self.timeline_rect = pygame.Rect(120, HEIGHT // 2 + 20, WIDTH - 240, 8)
        # Target year: random within life by default, or midpoint when configured
        if LIFE_TARGET_KIND == "midpoint":
            self.target_year = int((self.birth + self.death) / 2)
        else:
            self.target_year = random.randint(self.birth, self.death)
        # Start cursor at the leftmost visible bound
        self.cursor_x = self.year_to_x(self.min_year)
        self.holding_left = False
        self.holding_right = False
        self.state = "aim"
        self.selected_year = None
        self.score = 0
        # sounds
        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")
        self.snd_click = load_sound("click.wav")

        self.difficulty_multiplier = 1.0

    def year_to_x(self, year):
        # Map [min_year..max_year] to [timeline.left..timeline.right]
        span = self.max_year - self.min_year
        if span == 0:
            return self.timeline_rect.left
        t = (year - self.min_year) / span
        return int(self.timeline_rect.left + t * self.timeline_rect.width)

    def x_to_year(self, x):
        span = self.max_year - self.min_year
        if span == 0:
            return self.min_year
        t = (x - self.timeline_rect.left) / self.timeline_rect.width
        return self.min_year + t * span

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if self.state == "aim":
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    self.holding_left = True
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    self.holding_right = True
                elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.validate_selection()
            elif self.state == "result" and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                # Don't play sounds when clicking to continue
                self.validate_selection(play_sounds=False)
                self.game.complete_minigame(getattr(self, "score", 0), self._is_success())
        elif e.type == pygame.KEYUP and self.state == "aim":
            if e.key in (pygame.K_LEFT, pygame.K_a):
                self.holding_left = False
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.holding_right = False
        elif e.type == pygame.MOUSEBUTTONDOWN and self.state == "aim":
            if e.button == 1:  # Left click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.timeline_rect.collidepoint(mouse_x, mouse_y):
                    self.cursor_x = mouse_x
                    self.validate_selection()

    def update(self, dt):
        if self.state != "aim":
            return
        delta = 0
        if self.holding_left:
            delta -= self.CURSOR_SPEED * dt
        if self.holding_right:
            delta += self.CURSOR_SPEED * dt
        if delta != 0:
            x = clamp(self.cursor_x + delta, self.timeline_rect.left, self.timeline_rect.right)
            self.cursor_x = x

    def validate_selection(self, play_sounds=True):
        year = round(self.x_to_year(self.cursor_x))
        self.selected_year = int(year)
        error_years = abs(self.selected_year - self.target_year)
        visible_span = max(1, abs(self.max_year - self.min_year))
        precision = max(0.0, 1.0 - (error_years / (visible_span / 2)))
        self.score = int(100 * precision * self.difficulty_multiplier)
        self.state = "result"
        # play sfx
        if play_sounds:
            try:
                if self.snd_click:
                    self.snd_click.play()
                if self._is_success():
                    if self.snd_success:
                        self.snd_success.play()
                else:
                    if self.snd_fail:
                        self.snd_fail.play()
            except Exception:
                pass

    def _is_success(self):
        if self.selected_year is None:
            return False
        return abs(self.selected_year - self.target_year) <= self.TOLERANCE_YEARS

    def draw(self, screen):
        screen.fill(BG_COLOR)
        subtitle = f"Trouve l'année cible de {self.name}"
        blit_text_center(screen, self.title_font.render("Sur la frise: vise l'année", True, PRIMARY_COLOR), 70)
        blit_text_center(screen, self.ui_font.render(subtitle, True, SECONDARY_COLOR), 96)

        # Timeline background
        pygame.draw.rect(screen, (40, 40, 60), self.timeline_rect)
        pygame.draw.rect(screen, PRIMARY_COLOR, self.timeline_rect, 2)

        # Ticks and labels (birth and death only)
        for year in (self.birth, self.death):
            x = self.year_to_x(year)
            color = ACCENT_COLOR
            pygame.draw.line(screen, color, (x, self.timeline_rect.centery - 12), (x, self.timeline_rect.centery + 12), 3)
            label = self.large_font.render(str(year), True, color)
            screen.blit(label, label.get_rect(center=(x, self.timeline_rect.centery - 25)))

        # Target marker (only visible after validation)
        if self.state == "result":
            target_x = self.year_to_x(self.target_year)
            pygame.draw.line(screen, ACCENT_COLOR, (target_x, self.timeline_rect.centery - 16), (target_x, self.timeline_rect.centery + 16), 4)
            pygame.draw.circle(screen, ACCENT_COLOR, (int(target_x), self.timeline_rect.centery), 6)

        # Cursor
        cursor_color = ACCENT_COLOR if self.state == "aim" else (200, 200, 200)
        pygame.draw.circle(screen, cursor_color, (int(self.cursor_x), self.timeline_rect.centery), 8)


        # Instructions
        hint = "flèches directionnelles pour viser • ESPACE/clic pour valider" if self.state == "aim" else "ESPACE pour continuer"
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), HEIGHT - 26)
        draw_attempts(screen, self.game, pos=(None, 26))

        if self.state == "result":
            # Result overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            diff_years = abs(self.selected_year - self.target_year)
            is_success = diff_years <= self.TOLERANCE_YEARS
            
            # Result title
            if is_success:
                blit_text_center(screen, render_win_message(self.title_font), HEIGHT // 2 - 60)
            else:
                blit_text_center(screen, render_not_center_message(self.title_font_small), HEIGHT // 2 - 60)
            
            # Details
            chosen = self.large_font.render(f"Votre année: {self.selected_year}", True, PRIMARY_COLOR)
            exact_val = int(self.target_year) if isinstance(self.target_year, int) or float(self.target_year).is_integer() else self.target_year
            exact = self.large_font.render(f"Cible exacte: {exact_val}", True, PRIMARY_COLOR)
            result_color = GOOD_COLOR if is_success else BAD_COLOR
            diff = self.large_font.render(f"Écart: {int(round(diff_years))} ans", True, result_color)
            score_s = self.large_font.render(f"Score: {self.score}", True, PRIMARY_COLOR)
            
            blit_text_center(screen, chosen, HEIGHT // 2 - 20)
            blit_text_center(screen, exact, HEIGHT // 2 + 10)
            blit_text_center(screen, diff, HEIGHT // 2 + 40)
            blit_text_center(screen, score_s, HEIGHT // 2 + 70)


