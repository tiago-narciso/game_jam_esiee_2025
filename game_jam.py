import os
import sys
import pygame
import math

# ------------------ Config globale ------------------
WIDTH, HEIGHT = 960, 540
FPS = 120
TITLE = "Game Jam 2025 – Vous n'êtes pas au centre de l'histoire (Pygame)"

# --- Palette de couleurs ---
# https://lospec.com/palette-list/sweetie-16
BG_COLOR = (26, 28, 44)          # Fond sombre
PRIMARY_COLOR = (240, 240, 240)  # Texte principal
SECONDARY_COLOR = (158, 162, 173) # Texte secondaire
ACCENT_COLOR = (255, 107, 107)   # Accent (sélection, danger)
GOOD_COLOR = (169, 227, 141)     # Succès
BAD_COLOR = (255, 107, 107)      # Échec (identique à accent)

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
            ("La pomme de Newton", lambda: self.game.push_scene(NewtonScene(self.game))),
            ("Galerie d'images", lambda: self.game.push_scene(GalleryScene(self.game))),
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
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Menu principal", True, PRIMARY_COLOR), 120)
        for i, (label, _) in enumerate(self.items):
            col = ACCENT_COLOR if i == self.idx else PRIMARY_COLOR
            blit_text_center(screen, self.item_font.render(label, True, col), 220 + i * 44)
        blit_text_center(screen, self.hint_font.render("↑/↓ pour naviguer • Entrée pour valider • Échap pour quitter", True, SECONDARY_COLOR), HEIGHT - 40)

class CenterWordScene(Scene):
    WORD = "HISTOIRE"
    TOLERANCE = 2
    BASE_SPEED = 320      # px/s
    PADDING = 40          # marge autour du mot

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.word_font  = pygame.font.SysFont(None, 160, bold=True)
        self.ui_font    = pygame.font.SysFont(None, 22)

        # rendu du mot & géométrie
        self.word_surf = self.word_font.render(self.WORD, True, PRIMARY_COLOR)
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
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Arrête la barre au centre du mot", True, PRIMARY_COLOR), 60)
        hint = "ESPACE (ou clic) pour ARRÊTER • M: Menu" if self.state == "moving" else "R pour rejouer • M: Menu"
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), 92)

        # mot + ligne
        screen.blit(self.word_surf, self.word_rect.topleft)
        pygame.draw.line(screen, (80, 90, 110), (80, self.line_y), (WIDTH - 80, self.line_y), 2)

        # centre réel (repère fin)
        pygame.draw.line(screen, (90, 160, 210),
                         (self.true_center_x, self.line_y - 30),
                         (self.true_center_x, self.line_y + 30), 1)

        # curseur auto
        col = ACCENT_COLOR if self.result is None else (GOOD_COLOR if self.result == "win" else BAD_COLOR)
        draw_center_line(screen, int(self.cursor_x), self.line_y, 70, col, 3)
        pygame.draw.circle(screen, col, (int(self.cursor_x), self.line_y), 6)

        # HUD
        diff = abs(self.cursor_x - self.true_center_x)
        blit_text_center(screen, self.ui_font.render(
            f"Décalage: {int(diff)} px (Tolérance: {self.TOLERANCE}px)", True, PRIMARY_COLOR), HEIGHT - 28)

        # overlay résultat
        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)); screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Parfait ! Vous êtes au centre de l'histoire.", True, GOOD_COLOR)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (≤ {self.TOLERANCE}px)", True, PRIMARY_COLOR)
            else:
                t1 = self.title_font.render("Perdu : Vous n'êtes pas au centre de l'histoire.", True, BAD_COLOR)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (> {self.TOLERANCE}px)", True, PRIMARY_COLOR)
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
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Galerie d'images", True, PRIMARY_COLOR), 60)
        blit_text_center(screen, self.ui_font.render("←/→ pour naviguer • M: Menu", True, SECONDARY_COLOR), 92)

        img = self.images[self.idx]
        name = self.names[self.idx]
        rect = img.get_rect(center=(WIDTH//2, HEIGHT//2 + 10))
        screen.blit(img, rect)

        blit_text_center(screen, self.ui_font.render(name, True, PRIMARY_COLOR), rect.bottom + 24)

class NewtonScene(Scene):
    TOLERANCE = 5       # Tolérance en pixels pour le "milieu"
    FALL_SPEED = 150    # Vitesse de chute de la pomme en px/s

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 40, bold=True)
        self.ui_font = pygame.font.SysFont(None, 22)

        # Couleurs pour le style arcade
        self.tree_trunk_color = (139, 69, 19)
        self.tree_foliage_color = (34, 139, 34)
        self.newton_color = (70, 130, 180)
        self.apple_color = (255, 0, 0)

        # Géométrie de la scène
        self.ground_y = HEIGHT - 60
        self.tree_rect = pygame.Rect(WIDTH // 2 - 150, self.ground_y - 250, 300, 250)
        self.newton_rect = pygame.Rect(WIDTH // 2 - 20, self.ground_y - 80, 40, 80)
        
        self.start_y = self.tree_rect.top + 40
        self.end_y = self.newton_rect.top - 20
        self.target_y = self.start_y + (self.end_y - self.start_y) / 2

        # Sons
        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")
        self.snd_click = load_sound("click.wav")

        self.reset()

    def reset(self):
        self.state = "falling"  # falling -> stopped
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
                    self.validate()
                    self.state = "stopped"
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "falling":
                self.validate()
                self.state = "stopped"

    def update(self, dt):
        if self.state != "falling":
            return
        
        self.apple_y += self.FALL_SPEED * dt
        if self.apple_y >= self.end_y:
            self.apple_y = self.end_y
            self.validate()
            self.state = "stopped"

    def validate(self):
        if self.snd_click: self.snd_click.play()
        self.error_px = abs(self.apple_y - self.target_y)
        if self.error_px <= self.TOLERANCE:
            self.result = "win"
            if self.snd_success: self.snd_success.play()
        else:
            self.result = "lose"
            if self.snd_fail: self.snd_fail.play()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Arrêtez la pomme au milieu de sa chute !", True, PRIMARY_COLOR), 60)
        hint = "ESPACE (ou clic) pour ARRÊTER • M: Menu" if self.state == "falling" else "R pour rejouer • M: Menu"
        blit_text_center(screen, self.ui_font.render(hint, True, SECONDARY_COLOR), 92)

        # Sol
        pygame.draw.line(screen, self.tree_foliage_color, (0, self.ground_y), (WIDTH, self.ground_y), 5)

        # Arbre (style arcade)
        pygame.draw.rect(screen, self.tree_trunk_color, (self.tree_rect.centerx - 20, self.tree_rect.bottom - 100, 40, 100))
        pygame.draw.circle(screen, self.tree_foliage_color, (self.tree_rect.centerx, self.tree_rect.top + 100), 100)

        # Newton (style arcade)
        pygame.draw.rect(screen, self.newton_color, self.newton_rect)

        # Pomme
        apple_x = self.tree_rect.centerx + 30
        pygame.draw.circle(screen, self.apple_color, (apple_x, int(self.apple_y)), 15)

        # Ligne de milieu (aide visuelle)
        pygame.draw.line(screen, ACCENT_COLOR, (apple_x - 30, self.target_y), (apple_x + 30, self.target_y), 1)

        # HUD
        diff = abs(self.apple_y - self.target_y)
        blit_text_center(screen, self.ui_font.render(
            f"Décalage: {int(diff)} px (Tolérance: {self.TOLERANCE}px)", True, PRIMARY_COLOR), HEIGHT - 28)

        # Overlay résultat
        if self.state == "stopped":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Parfait ! En plein milieu de l'histoire.", True, GOOD_COLOR)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (≤ {self.TOLERANCE}px)", True, PRIMARY_COLOR)
            else:
                t1 = self.title_font.render("Perdu ! Ce n'était pas le milieu de l'histoire.", True, BAD_COLOR)
                t2 = self.ui_font.render(f"Erreur: {int(self.error_px)} px (> {self.TOLERANCE}px)", True, PRIMARY_COLOR)
            blit_text_center(screen, t1, HEIGHT // 2 - 10)
            blit_text_center(screen, t2, HEIGHT // 2 + 26)

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
