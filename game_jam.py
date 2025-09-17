import os
import sys
import pygame
import math
import random

# ------------------ Config globale ------------------
WIDTH, HEIGHT = 960, 540
FPS = 120
TITLE = "Game Jam 2025 – Vous n'êtes pas au centre de l'histoire (Pygame)"

WHITE = (240, 240, 240)
GRAY = (120, 130, 140)
DARK = (20, 24, 30)
ACCENT = (120, 200, 255)
GOOD = (120, 220, 160)
BAD = (250, 110, 110)

ASSETS_DIR = os.path.join("assets")
IMG_DIR = os.path.join(ASSETS_DIR, "images")
SND_DIR = os.path.join(ASSETS_DIR, "sounds")


# ------------------ Helpers ------------------
def clamp(x, a, b):
    return max(a, min(b, x))

def blit_text_center(surface, text_surf, y):
    rect = text_surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(text_surf, rect)

def draw_center_line(surface, x, y, height, color, thickness=3):
    pygame.draw.line(surface, color, (x, y - height//2), (x, y + height//2), thickness)

# Charger image si dispo, sinon rectangle de secours
def load_image(path, max_w=720, max_h=400):
    if os.path.isfile(path):
        img = pygame.image.load(path).convert_alpha()
        w, h = img.get_size()
        scale = min(max_w / w, max_h / h, 1.0)
        if scale != 1.0:
            img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
        return img
    else:
        # placeholder
        surf = pygame.Surface((max_w, int(max_h * 0.75)), pygame.SRCALPHA)
        surf.fill((40, 44, 52))
        pygame.draw.rect(surf, (70, 80, 90), surf.get_rect(), 3, border_radius=12)
        font = pygame.font.SysFont(None, 28, bold=True)
        txt = font.render("Image manquante", True, (200, 200, 200))
        surf.blit(txt, txt.get_rect(center=surf.get_rect().center))
        return surf

# Sons (facultatifs)
def load_sound(name):
    path = os.path.join(SND_DIR, name)
    if os.path.isfile(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None
    return None


# ------------------ Scenes ------------------
class Scene:
    def __init__(self, game):
        self.game = game
    def handle_event(self, e): pass
    def update(self, dt): pass
    def draw(self, screen): pass

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.items = [
            ("Au centre du mot", lambda: self.game.push_scene(CenterWordScene(self.game))),
            ("Galerie d'images", lambda: self.game.push_scene(GalleryScene(self.game))),
            ("Verre à remplir", lambda: self.game.push_scene(GlassFillScene(self.game))),
            ("BD – Trouver le milieu", lambda: self.game.push_scene(ComicScene(self.game))),
            ("Quitter", lambda: self.game.quit()),
        ]
        self.idx = 0
        self.title_font = pygame.font.SysFont(None, 48, bold=True)
        self.item_font = pygame.font.SysFont(None, 32)
        self.hint_font = pygame.font.SysFont(None, 20)

        self.snd_move = load_sound("click.wav")

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.game.quit()
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.idx = (self.idx - 1) % len(self.items)
                if self.snd_move: self.snd_move.play()
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.idx = (self.idx + 1) % len(self.items)
                if self.snd_move: self.snd_move.play()
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                _, fn = self.items[self.idx]
                fn()

    def draw(self, screen):
        screen.fill(DARK)
        blit_text_center(screen, self.title_font.render("Menu principal", True, WHITE), 120)
        for i, (label, _) in enumerate(self.items):
            col = ACCENT if i == self.idx else WHITE
            blit_text_center(screen, self.item_font.render(label, True, col), 220 + i * 44)
        blit_text_center(screen, self.hint_font.render("↑/↓ pour naviguer • Entrée pour valider • Échap pour quitter", True, GRAY), HEIGHT - 40)

class CenterWordScene(Scene):
    WORD = "HISTOIRE"
    TOLERANCE = 2
    BASE_SPEED = 420      # px/s
    PADDING = 40          # marge autour du mot

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.word_font  = pygame.font.SysFont(None, 160, bold=True)
        self.ui_font    = pygame.font.SysFont(None, 22)

        # rendu du mot & géométrie
        self.word_surf = self.word_font.render(self.WORD, True, WHITE)
        self.word_rect = self.word_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        self.true_center_x = self.word_rect.centerx
        self.line_y = self.word_rect.bottom + 28

        # bornes de déplacement auto (autour du mot)
        self.min_x = self.word_rect.left  - self.PADDING
        self.max_x = self.word_rect.right + self.PADDING

        # sons (optionnels)
        self.snd_success = load_sound("success.wav")
        self.snd_fail    = load_sound("fail.wav")
        self.snd_click   = load_sound("click.wav")

        self.reset()

    def reset(self):
        self.state = "moving"   # moving -> stopped
        self.cursor_x = self.min_x
        self.dir = +1
        self.result = None      # None | "win" | "lose"
        self.error_px = None
        self.time_acc = 0.0     # pour modulation douce de la vitesse

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif e.key == pygame.K_r and self.state == "stopped":
                self.reset()
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == "moving":
                    self.validate(); self.state = "stopped"
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "moving":
                self.validate(); self.state = "stopped"

    def update(self, dt):
        if self.state != "moving":
            return
        # modulation douce de vitesse ±10%
        self.time_acc += dt
        speed = self.BASE_SPEED * (1.0 + 0.10 * math.sin(self.time_acc * 4.0))

        self.cursor_x += self.dir * speed * dt

        if self.cursor_x >= self.max_x:
            self.cursor_x = self.max_x
            self.dir = -1
        elif self.cursor_x <= self.min_x:
            self.cursor_x = self.min_x
            self.dir = +1

    def validate(self):
        if self.snd_click: self.snd_click.play()
        self.error_px = abs(self.cursor_x - self.true_center_x)
        if self.error_px <= self.TOLERANCE:
            self.result = "win"
            if self.snd_success: self.snd_success.play()
        else:
            self.result = "lose"
            if self.snd_fail: self.snd_fail.play()

    def draw(self, screen):
        screen.fill(DARK)
        blit_text_center(screen, self.title_font.render("Arrête la barre au centre du mot", True, WHITE), 60)
        hint = "ESPACE (ou clic) pour ARRÊTER • M: Menu" if self.state == "moving" else "R pour rejouer • M: Menu"
        blit_text_center(screen, self.ui_font.render(hint, True, GRAY), 92)

        # mot + ligne
        screen.blit(self.word_surf, self.word_rect.topleft)
        pygame.draw.line(screen, (80, 90, 110), (80, self.line_y), (WIDTH - 80, self.line_y), 2)

        # centre réel (repère fin)
        pygame.draw.line(screen, (90, 160, 210),
                         (self.true_center_x, self.line_y - 30),
                         (self.true_center_x, self.line_y + 30), 1)

        # curseur auto
        col = ACCENT if self.result is None else (GOOD if self.result == "win" else BAD)
        draw_center_line(screen, int(self.cursor_x), self.line_y, 70, col, 3)
        pygame.draw.circle(screen, col, (int(self.cursor_x), self.line_y), 6)

        # HUD
        diff = abs(self.cursor_x - self.true_center_x)
        blit_text_center(screen, self.ui_font.render(
            f"Décalage: {int(diff)} px (Tolérance: {self.TOLERANCE}px)", True, WHITE), HEIGHT - 28)

        # overlay résultat
        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)); screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Parfait ! Vous êtes au centre de l'histoire.", True, GOOD)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (≤ {self.TOLERANCE}px)", True, WHITE)
            else:
                t1 = self.title_font.render("Perdu : Vous n'êtes pas au centre de l'histoire.", True, BAD)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (> {self.TOLERANCE}px)", True, WHITE)
            blit_text_center(screen, t1, HEIGHT//2 - 10)
            blit_text_center(screen, t2, HEIGHT//2 + 26)

class GalleryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)

        # liste d'images dans assets/images
        if os.path.isdir(IMG_DIR):
            files = [f for f in os.listdir(IMG_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))]
            files.sort()
            self.paths = [os.path.join(IMG_DIR, f) for f in files]
        else:
            self.paths = []

        # toujours avoir au moins un placeholder
        if not self.paths:
            self.images = [load_image("__placeholder__", 720, 400)]
            self.names = ["(placer vos images dans assets/images)"]
        else:
            self.images = [load_image(p, 720, 400) for p in self.paths]
            self.names = [os.path.basename(p) for p in self.paths]

        self.idx = 0
        self.snd_click = load_sound("click.wav")

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_m or e.key == pygame.K_ESCAPE:
                self.game.pop_scene()
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.idx = (self.idx + 1) % len(self.images)
                if self.snd_click: self.snd_click.play()
            elif e.key in (pygame.K_LEFT, pygame.K_a):
                self.idx = (self.idx - 1) % len(self.images)
                if self.snd_click: self.snd_click.play()

    def draw(self, screen):
        screen.fill(DARK)
        blit_text_center(screen, self.title_font.render("Galerie d'images", True, WHITE), 60)
        blit_text_center(screen, self.ui_font.render("←/→ pour naviguer • M: Menu", True, GRAY), 92)

        img = self.images[self.idx]
        name = self.names[self.idx]
        rect = img.get_rect(center=(WIDTH//2, HEIGHT//2 + 10))
        screen.blit(img, rect)

        blit_text_center(screen, self.ui_font.render(name, True, WHITE), rect.bottom + 24)

class GlassFillScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)
        self.level = 0.0     # 0..1
        self.speed = 0.35    # vitesse de remplissage par seconde
        self.state = "play"  # play | win | lose

        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")

        # géométrie du "verre"
        self.glass_rect = pygame.Rect(0, 0, 160, 260)
        self.glass_rect.center = (WIDTH//2, HEIGHT//2 + 40)
        self.fill_margin = 16  # marge intérieure pour l'eau

    def reset(self):
        self.level = 0.0
        self.state = "play"

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif e.key == pygame.K_r and self.state != "play":
                self.reset()

    def update(self, dt):
        if self.state != "play":
            return
        keys = pygame.key.get_pressed()

        # Espace maintenu = on remplit
        if keys[pygame.K_SPACE]:
            self.level += self.speed * dt
        else:
            # légère évaporation pour ajouter du contrôle
            self.level = max(0.0, self.level - 0.15 * dt)

        self.level = clamp(self.level, 0.0, 1.15)  # autorise un léger dépassement pour l'échec

        # conditions de victoire/défaite
        if self.level >= 1.0 and self.level <= 1.02:
            self.state = "win"
            if self.snd_success: self.snd_success.play()
        elif self.level > 1.05:
            self.state = "lose"
            if self.snd_fail: self.snd_fail.play()

    def draw(self, screen):
        screen.fill(DARK)
        blit_text_center(screen, self.title_font.render("Verre à remplir", True, WHITE), 60)
        blit_text_center(screen, self.ui_font.render("Maintiens ESPACE pour remplir • Vise le trait • M: Menu", True, GRAY), 92)

        # Verre
        pygame.draw.rect(screen, (200, 200, 200), self.glass_rect, width=3, border_radius=10)

        # Trait objectif (niveau 100%)
        target_y = self.glass_rect.top + 20
        pygame.draw.line(screen, (220, 180, 80), (self.glass_rect.left + 6, target_y),
                         (self.glass_rect.right - 6, target_y), 3)

        # Eau
        inner = self.glass_rect.inflate(-self.fill_margin, -self.fill_margin)
        max_h = inner.height
        h = clamp(int(max_h * clamp(self.level, 0, 1.15)), 0, int(max_h * 1.15))
        water_rect = pygame.Rect(inner.left, inner.bottom - h, inner.width, h)
        pygame.draw.rect(screen, (80, 160, 255), water_rect, border_radius=6)

        # HUD
        perc = int(clamp(self.level, 0.0, 1.15) * 100)
        blit_text_center(screen, self.ui_font.render(f"Niveau: {perc}%", True, WHITE), HEIGHT - 28)

        if self.state != "play":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.state == "win":
                t1 = self.title_font.render("Parfait !", True, GOOD)
                t2 = self.ui_font.render("Pile au niveau du trait. R pour rejouer • M pour menu", True, WHITE)
            else:
                t1 = self.title_font.render("Débordement !", True, BAD)
                t2 = self.ui_font.render("Trop rempli… R pour rejouer • M pour menu", True, WHITE)
            blit_text_center(screen, t1, HEIGHT//2 - 10)
            blit_text_center(screen, t2, HEIGHT//2 + 26)

class ComicScene(Scene):
    GRID_COLS = 3
    GRID_ROWS = 2
    HIGHLIGHT_SPEED = 8.0  # cases par seconde

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)

        # --- Chargement des images depuis assets/images/comic ---
        self.comic_dir = os.path.join(IMG_DIR, "comic")
        os.makedirs(self.comic_dir, exist_ok=True)

        valid_ext = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        all_files = [f for f in os.listdir(self.comic_dir)
                     if f.lower().endswith(valid_ext)]
        all_files.sort()  # tri alphabétique = ordre "chronologique" de l'histoire

        # Debug console utile
        print("[ComicScene] Dossier:", self.comic_dir)
        print("[ComicScene] Fichiers détectés (triés):", all_files)

        needed = self.GRID_COLS * self.GRID_ROWS
        if not all_files:
            # Pas d’images → placeholders
            self.paths = []
            self.images = [load_image("__placeholder__", 240, 200) for _ in range(needed)]
            self.names = ["(placez vos images dans assets/images/comic)"] * needed
        else:
            # On prend au plus 'needed' images
            selected = all_files[:needed]
            self.paths = [os.path.join(self.comic_dir, f) for f in selected]
            self.images = [load_image(p, 240, 200) for p in self.paths]
            self.names = selected

        # Détermination du "milieu de l'histoire" après tri
        self.story_middle_idx = len(self.paths) // 2 if self.paths else None
        self.story_middle_path = self.paths[self.story_middle_idx] if self.paths else None
        print("[ComicScene] Milieu de l'histoire:", self.story_middle_path)

        # Ordre d'affichage mélangé (indices vers self.paths/self.images)
        self.grid_order = list(range(len(self.images)))
        random.shuffle(self.grid_order)
        print("[ComicScene] Ordre affiché (mélangé):")
        for i, idx in enumerate(self.grid_order):
            label = self.names[idx] if self.names else "placeholder"
            print(f"  grid {i} → {label}")

        # Highlight & état
        self.current_idx = 0  # index de case dans la grille (0..N-1)
        self.timer = 0.0
        self.state = "moving"  # moving | stopped
        self.result = None

        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif e.key == pygame.K_r and self.state == "stopped":
                self.reset()
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == "moving":
                    self.validate()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "moving":
                self.validate()

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
            self.current_idx = (self.current_idx + 1) % max(1, len(self.images))

    def validate(self):
        # Stoppe l’animation et décide victoire/défaite
        self.state = "stopped"
        if not self.paths:
            self.result = "lose"
            return

        # current_idx = position du highlight dans la grille mélangée
        shown_img_idx = self.grid_order[self.current_idx]   # index réel (dans paths/images)
        shown_path = self.paths[shown_img_idx]
        is_middle = (shown_path == self.story_middle_path)

        # Debug console pour vérifier
        print("[ComicScene] Shown path:", shown_path)
        print("[ComicScene] Middle path:", self.story_middle_path)

        self.result = "win" if is_middle else "lose"
        if self.result == "win":
            if self.snd_success: self.snd_success.play()
        else:
            if self.snd_fail: self.snd_fail.play()

    def draw(self, screen):
        screen.fill(DARK)
        blit_text_center(
            screen,
            self.title_font.render(" Quel est le milieu de l'histoire", True, WHITE),
            50
        )
        blit_text_center(screen, self.ui_font.render("M: Menu  •  R: Rejouer", True, GRAY), 80)

        # Calcul de la grille
        margin_x, margin_y = 60, 120
        spacing_x, spacing_y = 20, 20
        if self.GRID_COLS <= 0: self.GRID_COLS = 1
        if self.GRID_ROWS <= 0: self.GRID_ROWS = 1

        w = (WIDTH - 2 * margin_x - (self.GRID_COLS - 1) * spacing_x) // self.GRID_COLS
        h = (HEIGHT - 2 * margin_y - (self.GRID_ROWS - 1) * spacing_y) // self.GRID_ROWS

        # Affichage des cases
        k = 0
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                if k >= len(self.images):
                    break
                grid_idx = k
                img_idx = self.grid_order[grid_idx]
                img = self.images[img_idx]

                rect = pygame.Rect(
                    margin_x + c * (w + spacing_x),
                    margin_y + r * (h + spacing_y),
                    w, h
                )
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)

                # cadre fin
                pygame.draw.rect(screen, (80, 90, 110), rect, 2, border_radius=10)
                # highlight si sélectionnée
                if grid_idx == self.current_idx:
                    pygame.draw.rect(screen, ACCENT, rect, 5, border_radius=12)

                k += 1

        # Overlay résultat
        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Bravo ! Tu es bien au milieu de l'histoire", True, GOOD)
                t2 = self.ui_font.render("R pour rejouer • M pour menu", True, WHITE)
            else:
                t1 = self.title_font.render("Vous n'etes pas au milieu de l'histoire!!", True, BAD)
                ans = os.path.basename(self.story_middle_path) if self.story_middle_path else "N/A"
                t2 = self.ui_font.render(f"La case du milieu était : {ans}  •  R pour rejouer • M pour menu", True, WHITE)
            blit_text_center(screen, t1, HEIGHT//2 - 10)

# ------------------ Boucle principale ------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # audio (si init échoue, on continue sans son)
        try:
            pygame.mixer.init()
        except Exception:
            pass

        self.scenes = []
        self.running = True
        self.push_scene(MenuScene(self))

    def push_scene(self, scene):
        self.scenes.append(scene)

    def pop_scene(self):
        if self.scenes:
            self.scenes.pop()

    def top_scene(self):
        return self.scenes[-1] if self.scenes else None

    def quit(self):
        self.running = False

    def run(self):
        while self.running and self.top_scene() is not None:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.quit()
                else:
                    sc = self.top_scene()
                    if sc: sc.handle_event(e)
            sc = self.top_scene()
            if sc:
                sc.update(dt)
                sc.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Game().run()
