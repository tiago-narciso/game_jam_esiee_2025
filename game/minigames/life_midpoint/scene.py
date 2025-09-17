import random
import pygame
from ...core import Scene
from ...config import WIDTH, HEIGHT, PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, ACCENT_COLOR, GOOD_COLOR, BAD_COLOR, CELEBRITIES, LIFE_KEY_SPEED, LIFE_TIMELINE_PADDING_YEARS, LIFE_TARGET_KIND
from ...utils import blit_text_center, clamp


class LifeMidpointScene(Scene):
    CURSOR_SPEED = LIFE_KEY_SPEED  # pixels per second for keyboard

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)
        self.large_font = pygame.font.SysFont(None, 28)
        self.person = random.choice(CELEBRITIES)
        name, birth, death = self.person
        self.name = name
        self.birth = birth
        self.death = death
        self.min_year = self.birth - LIFE_TIMELINE_PADDING_YEARS
        self.max_year = self.death + LIFE_TIMELINE_PADDING_YEARS
        self.timeline_rect = pygame.Rect(120, HEIGHT // 2 + 20, WIDTH - 240, 6)
        # Target year: random within life by default, or midpoint when configured
        if LIFE_TARGET_KIND == "midpoint":
            self.target_year = (self.birth + self.death) / 2
        else:
            self.target_year = random.randint(self.birth, self.death)
        # Start cursor at the leftmost visible bound
        self.cursor_x = self.year_to_x(self.min_year)
        self.holding_left = False
        self.holding_right = False
        self.state = "aim"
        self.selected_year = None
        self.score = 0

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
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif self.state == "aim":
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    self.holding_left = True
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    self.holding_right = True
                elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.validate_selection()
        elif e.type == pygame.KEYUP and self.state == "aim":
            if e.key in (pygame.K_LEFT, pygame.K_a):
                self.holding_left = False
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.holding_right = False
        # Mouse input disabled for this game mode

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

    def validate_selection(self):
        year = round(self.x_to_year(self.cursor_x))
        self.selected_year = int(year)
        error_years = abs(self.selected_year - self.target_year)
        visible_span = max(1, abs(self.max_year - self.min_year))
        precision = max(0.0, 1.0 - (error_years / (visible_span / 2)))
        self.score = int(100 * precision)
        self.state = "result"

    def draw(self, screen):
        screen.fill(BG_COLOR)
        subtitle = f"Trouve l'année cible de {self.name}"
        blit_text_center(screen, self.title_font.render("Sur la frise: vise l'année", True, PRIMARY_COLOR), 70)
        blit_text_center(screen, self.ui_font.render(subtitle, True, SECONDARY_COLOR), 96)

        # Timeline
        pygame.draw.line(screen, PRIMARY_COLOR, self.timeline_rect.topleft, self.timeline_rect.topright, self.timeline_rect.height)

        # Ticks and labels (birth, death, and padded bounds)
        for year in (self.min_year, self.birth, self.death, self.max_year):
            x = self.year_to_x(year)
            pygame.draw.line(screen, SECONDARY_COLOR, (x, self.timeline_rect.centery - 8), (x, self.timeline_rect.centery + 8), 2)
            label = self.large_font.render(str(year), True, PRIMARY_COLOR)
            screen.blit(label, label.get_rect(center=(x, self.timeline_rect.centery - 18)))

        # Target marker (only visible after validation)
        if self.state == "result":
            target_x = self.year_to_x(self.target_year)
            pygame.draw.line(screen, ACCENT_COLOR, (target_x, self.timeline_rect.centery - 14), (target_x, self.timeline_rect.centery + 14), 2)

        # Cursor
        cursor_color = ACCENT_COLOR if self.state == "aim" else (200, 200, 200)
        pygame.draw.circle(screen, cursor_color, (int(self.cursor_x), self.timeline_rect.centery), 8)

        # Instructions
        hint = "←/→ pour viser • ESPACE pour valider • M: menu" if self.state == "aim" else "Appuyez sur ESPACE pour continuer"
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), HEIGHT - 26)

        if self.state == "result":
            chosen = self.large_font.render(f"Votre année: {self.selected_year}", True, PRIMARY_COLOR)
            exact_val = int(self.target_year) if isinstance(self.target_year, int) or float(self.target_year).is_integer() else self.target_year
            exact = self.large_font.render(f"Cible exacte: {exact_val}", True, PRIMARY_COLOR)
            diff_years = abs(self.selected_year - self.target_year)
            diff = self.large_font.render(f"Écart: à {int(round(diff_years))} ans près !", True, GOOD_COLOR if diff_years <= 2 else BAD_COLOR)
            score_s = self.large_font.render(f"Score: {self.score}", True, PRIMARY_COLOR)
            blit_text_center(screen, chosen, HEIGHT // 2 - 40)
            blit_text_center(screen, exact, HEIGHT // 2 - 10)
            blit_text_center(screen, diff, HEIGHT // 2 + 20)
            blit_text_center(screen, score_s, HEIGHT // 2 + 50)


