import math
import os
import random
import pygame
from ...core import Scene
from ...config import WIDTH, HEIGHT, PRIMARY_COLOR, BG_COLOR, ACCENT_COLOR, GOOD_COLOR, BAD_COLOR, SECONDARY_COLOR, IMG_DIR, FONT_PATH
from ...utils import blit_text_center, load_image, load_sound, render_not_center_message, draw_attempts
from .data import IPHONE_MODELS


class TimelineMiddleScene(Scene):
    SCROLL_SPEED = 300
    CARD_W = 320
    CARD_H = 220
    GAP = 28

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(FONT_PATH, 38)
        self.ui_font = pygame.font.Font(FONT_PATH, 22)
        self.card_title_font = pygame.font.Font(FONT_PATH, 26)
        self.card_desc_font = pygame.font.Font(FONT_PATH, 24)

        self.cards = self._build_cards(IPHONE_MODELS)
        self.scroll_x = 0.0
        self.state = "scrolling"
        self.result = None
        self.error_idx = None
        # Middle year is arithmetic midpoint between min and max years (not median of entries)
        years_sorted = sorted([c["year"] for c in self.cards])
        if years_sorted:
            self.year_min = years_sorted[0]
            self.year_max = years_sorted[-1]
            self.middle_year_value = (self.year_min + self.year_max) / 2.0
        else:
            self.year_min = 0
            self.year_max = 0
            self.middle_year_value = 0.0

        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")
        self.snd_click = load_sound("click.wav")

    def _build_cards(self, items):
        # Shuffle items so timeline is not ordered
        items_list = list(items)
        random.shuffle(items_list)
        cards = []
        for year, label in items_list:
            # Image path convention: IMG_DIR/timeline/iphone/<label>.png (spaces allowed)
            img_path = os.path.join(IMG_DIR, "timeline", "iphone", f"{label}.png")
            img = load_image(img_path, max_w=self.CARD_W - 24, max_h=120)
            cards.append({
                "year": year,
                "label": label,
                "image": img,
            })
        return cards

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif e.key == pygame.K_r and self.state == "stopped":
                self._reset()
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == "scrolling":
                    self._validate(); self.state = "stopped"
                elif self.state == "stopped":
                    score = getattr(self, "score", 0)
                    success = (self.result == "win")
                    self.game.complete_minigame(score, success)
            elif self.state == "stopped":
                score = getattr(self, "score", 0)
                success = (self.result == "win")
                self.game.complete_minigame(score, success)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "scrolling":
                self._validate(); self.state = "stopped"
            elif self.state == "stopped":
                score = getattr(self, "score", 0)
                self.game.complete_minigame(score, self.result == "win")

    def _reset(self):
        self.scroll_x = 0.0
        self.state = "scrolling"
        self.result = None
        self.error_idx = None

    def update(self, dt):
        if self.state != "scrolling":
            return
        # Scroll cards from right to left in a loop
        self.scroll_x += self.SCROLL_SPEED * dt
        total_len = len(self.cards)
        card_span = self.CARD_W + self.GAP
        # Keep scroll within one loop length for numeric stability
        loop_len = total_len * card_span
        if loop_len > 0:
            self.scroll_x = self.scroll_x % loop_len

    def _validate(self):
        if self.snd_click:
            self.snd_click.play()
        # Which card is at the screen center? Match the draw logic exactly
        card_span = self.CARD_W + self.GAP
        total = len(self.cards)
        if total == 0:
            return
        # Use same decomposition as draw: integer index and fractional offset within a span
        first_index = int(self.scroll_x // card_span) % total
        frac = (self.scroll_x % card_span) / card_span  # in [0,1)
        nearest_idx = (first_index + int(round(frac))) % total
        selected_year = self.cards[nearest_idx]["year"]

        # Win if selected year equals exact arithmetic midpoint
        if abs(selected_year - self.middle_year_value) == 0:
            self.result = "win"
            if self.snd_success:
                self.snd_success.play()
        else:
            self.result = "lose"
            if self.snd_fail:
                self.snd_fail.play()
        # Score scaled by distance to arithmetic midpoint
        span = max(1.0, float(self.year_max - self.year_min))
        year_range_half = max(1.0, span / 2.0)
        year_distance = abs(selected_year - self.middle_year_value)
        raw = int(100 * max(0.0, 1.0 - (year_distance / year_range_half)))
        self.score = max(0, min(100, raw))

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Stoppe au milieu de l'histoire (iPhone)", True, PRIMARY_COLOR), 56)
        hint = "ESPACE (ou clic) pour ARRÊTER • M: Menu" if self.state == "scrolling" else "ESPACE/clic pour continuer • R pour rejouer"
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), 86)
        draw_attempts(screen, self.game, pos=(None, 26))

        # Draw cards horizontally with current scroll offset
        card_span = self.CARD_W + self.GAP
        start_x = - (self.scroll_x % card_span)
        y = HEIGHT // 2 - self.CARD_H // 2 + 10
        # Draw extra copies on both sides to avoid early popping
        padding = 2
        total_draw = len(self.cards) + padding * 2 + 1
        first_index = int(self.scroll_x // card_span) % len(self.cards)
        for n in range(-padding, -padding + total_draw):
            idx = (first_index + n) % len(self.cards)
            card = self.cards[idx]
            x = start_x + n * card_span - self.CARD_W // 2 + WIDTH // 2
            rect = pygame.Rect(int(x), int(y), self.CARD_W, self.CARD_H)
            # Cull strictly off-screen so cards disappear only when fully outside
            if rect.right <= 0 or rect.left >= WIDTH:
                continue
            # Card background
            pygame.draw.rect(screen, (40, 45, 55), rect, border_radius=10)
            pygame.draw.rect(screen, (80, 90, 100), rect, width=2, border_radius=10)
            # Image
            img = card["image"]
            if img:
                img_rect = img.get_rect(midtop=(rect.centerx, rect.top + 14))
                screen.blit(img, img_rect)
            # Text with backdrop and slight shadow for readability
            label_surf = self.card_desc_font.render(card["label"], True, (240, 245, 255))
            label_rect = label_surf.get_rect(midtop=(rect.centerx, rect.bottom - 34))
            # Backdrop band
            band_h = 40
            band_rect = pygame.Rect(rect.left + 6, rect.bottom - band_h - 6, rect.width - 12, band_h)
            overlay = pygame.Surface((band_rect.width, band_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, band_rect.topleft)
            # Shadow
            shadow = self.card_desc_font.render(card["label"], True, (0, 0, 0))
            screen.blit(shadow, (label_rect.x + 1, label_rect.y + 1))
            # Text
            screen.blit(label_surf, label_rect)

        # Draw center cursor on top of images
        cursor_y0 = 120
        cursor_y1 = HEIGHT - 60
        pygame.draw.line(screen, ACCENT_COLOR, (WIDTH // 2, cursor_y0), (WIDTH // 2, cursor_y1), 2)

        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Parfait !", True, GOOD_COLOR)
                t2 = self.ui_font.render("Tu as stoppé au milieu de l'histoire.", True, PRIMARY_COLOR)
            else:
                t1 = render_not_center_message(self.title_font)
                t2 = self.ui_font.render("Ce n'était pas le milieu exact.", True, PRIMARY_COLOR)
            blit_text_center(screen, t1, HEIGHT // 2 - 8)
            blit_text_center(screen, t2, HEIGHT // 2 + 24)
            blit_text_center(screen, self.ui_font.render(f"Score: {getattr(self, 'score', 0)}", True, PRIMARY_COLOR), HEIGHT // 2 + 48)



