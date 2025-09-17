import os
import random
import pygame
from ...core import Scene
from ...config import WIDTH, HEIGHT, PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, ACCENT_COLOR, GOOD_COLOR, BAD_COLOR, IMG_DIR
from ...utils import blit_text_center, load_image, load_sound


class ComicScene(Scene):
    GRID_COLS = 3
    GRID_ROWS = 2
    HIGHLIGHT_SPEED = 8.0  # cells per second

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)

        # Load images from assets/images/comic
        self.comic_dir = os.path.join(IMG_DIR, "comic")
        os.makedirs(self.comic_dir, exist_ok=True)

        valid_ext = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        all_files = [f for f in os.listdir(self.comic_dir) if f.lower().endswith(valid_ext)]
        all_files.sort()

        needed = self.GRID_COLS * self.GRID_ROWS
        if not all_files:
            self.paths = []
            self.images = [load_image("__placeholder__", 240, 200) for _ in range(needed)]
            self.names = ["(placez vos images dans assets/images/comic)"] * needed
        else:
            selected = all_files[:needed]
            self.paths = [os.path.join(self.comic_dir, f) for f in selected]
            self.images = [load_image(p, 240, 200) for p in self.paths]
            self.names = selected

        # Story middle based on alphabetical order after sorting
        self.story_middle_idx = len(self.paths) // 2 if self.paths else None
        self.story_middle_path = self.paths[self.story_middle_idx] if self.paths else None

        # Grid order is shuffled for display
        self.grid_order = list(range(len(self.images)))
        random.shuffle(self.grid_order)

        # Animation/highlight state
        self.current_idx = 0
        self.timer = 0.0
        self.state = "moving"  # moving | stopped
        self.result = None

        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")
        self.snd_click = load_sound("click.wav")

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif e.key == pygame.K_r and self.state == "stopped":
                self.reset()
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == "moving":
                    self.validate()
                elif self.state == "stopped":
                    score = getattr(self, "score", 0)
                    success = (self.result == "win")
                    self.game.complete_minigame(score, success)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "moving":
                self.validate()
            elif self.state == "stopped":
                score = getattr(self, "score", 0)
                success = (self.result == "win")
                self.game.complete_minigame(score, success)

    def reset(self):
        self.state = "moving"
        self.result = None
        self.current_idx = 0
        self.timer = 0.0

    def update(self, dt):
        if self.state != "moving":
            return
        self.timer += dt
        if self.timer >= 1.0 / self.HIGHLIGHT_SPEED:
            self.timer = 0.0
            total = max(1, len(self.images))
            self.current_idx = (self.current_idx + 1) % total

    def validate(self):
        if self.snd_click:
            self.snd_click.play()
        self.state = "stopped"
        if not self.paths:
            self.result = "lose"
            return
        shown_img_idx = self.grid_order[self.current_idx]
        shown_path = self.paths[shown_img_idx]
        is_middle = (shown_path == self.story_middle_path)
        self.result = "win" if is_middle else "lose"
        if self.result == "win":
            if self.snd_success:
                self.snd_success.play()
        else:
            if self.snd_fail:
                self.snd_fail.play()
        # Score: 100 if correct middle, else 0
        self.score = 100 if is_middle else 0

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Quel est le milieu de l'histoire ?", True, PRIMARY_COLOR), 50)
        hint_top = "M: Menu  •  R: Rejouer" if self.state != "moving" else "M: Menu"
        blit_text_center(screen, self.ui_font.render(hint_top, True, SECONDARY_COLOR), 80)

        # Grid geometry
        margin_x, margin_y = 60, 120
        spacing_x, spacing_y = 20, 20
        cols = max(1, int(self.GRID_COLS))
        rows = max(1, int(self.GRID_ROWS))
        w = (WIDTH - 2 * margin_x - (cols - 1) * spacing_x) // cols
        h = (HEIGHT - 2 * margin_y - (rows - 1) * spacing_y) // rows

        k = 0
        for r in range(rows):
            for c in range(cols):
                if k >= len(self.images):
                    break
                grid_idx = k
                img_idx = self.grid_order[grid_idx]
                img = self.images[img_idx]
                rect = pygame.Rect(
                    margin_x + c * (w + spacing_x),
                    margin_y + r * (h + spacing_y),
                    w, h,
                )
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)
                # border
                pygame.draw.rect(screen, (80, 90, 110), rect, 2, border_radius=10)
                if grid_idx == self.current_idx:
                    pygame.draw.rect(screen, ACCENT_COLOR, rect, 5, border_radius=12)
                k += 1

        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Bravo ! Tu es bien au milieu de l'histoire", True, GOOD_COLOR)
                t2 = self.ui_font.render("ESPACE/clic pour continuer • R pour rejouer • M pour menu", True, PRIMARY_COLOR)
            else:
                t1 = self.title_font.render("Vous n'êtes pas au milieu de l'histoire !!", True, BAD_COLOR)
                ans = os.path.basename(self.story_middle_path) if self.story_middle_path else "N/A"
                t2 = self.ui_font.render(f"La case du milieu était : {ans}  •  ESPACE/clic pour continuer • R pour rejouer • M pour menu", True, PRIMARY_COLOR)
            blit_text_center(screen, t1, HEIGHT // 2 - 10)
            blit_text_center(screen, t2, HEIGHT // 2 + 26)
            # Score display for consistency
            score_text = self.ui_font.render(f"Score: {getattr(self, 'score', 0)}", True, PRIMARY_COLOR)
            blit_text_center(screen, score_text, HEIGHT // 2 + 52)



