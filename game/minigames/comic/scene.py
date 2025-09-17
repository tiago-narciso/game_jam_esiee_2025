import os
import random
import pygame
from ...core import Scene
from ...config import GAME_WIDTH, GAME_HEIGHT, PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, ACCENT_COLOR, GOOD_COLOR, BAD_COLOR, IMG_DIR, FONT_PATH
from ...utils import blit_text_center, load_image, load_sound, draw_attempts


def blit_fit(surface, img, rect):
    """Blitte l'image en conservant le ratio pour remplir au mieux rect (letterbox)."""
    iw, ih = img.get_size()
    rw, rh = rect.width, rect.height
    if iw == 0 or ih == 0 or rw <= 0 or rh <= 0:
        return
    scale = min(rw / iw, rh / ih)
    tw, th = int(iw * scale), int(ih * scale)
    if scale != 1.0:
        img = pygame.transform.smoothscale(img, (tw, th))
    dst = img.get_rect(center=rect.center)
    surface.blit(img, dst)


class ComicScene(Scene):
    """
    Niveau BD 7 cases : layout 4 (haut) + 3 (bas centré).
    Highlight animé ; validation quand la VRAIE case du milieu (tri alphabétique) est surlignée.
    """
    TARGET_COUNT = 7
    HIGHLIGHT_SPEED = 6.0   # cases / seconde (plus lisible)
    TILE_TARGET_H = 230     # hauteur visuelle d'une vignette (approx.)
    TILE_ASPECT = 3/4       # ratio "portrait" typique d'une case BD (ajuste si besoin)
    TILE_PADDING = 14       # marge intérieure du cadre
    GUTTER_X = 32           # espacement horizontal
    GUTTER_Y = 34           # espacement vertical
    MARGIN_TOP = 140
    MARGIN_SIDE = 60
    MARGIN_BOTTOM = 40   
    
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(FONT_PATH, 40)
        self.ui_font = pygame.font.Font(FONT_PATH, 22)

        # --- chargement images ---
        self.comic_dir = os.path.join(IMG_DIR, "comic")
        os.makedirs(self.comic_dir, exist_ok=True)
        valid_ext = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        files = [f for f in os.listdir(self.comic_dir) if f.lower().endswith(valid_ext)]
        files.sort()
        selected = files[:self.TARGET_COUNT]

        if not selected:
            self.paths = []
            self.images = [load_image("__placeholder__", 400, 400) for _ in range(self.TARGET_COUNT)]
            self.names = ["(placez vos images dans assets/images/comic)"] * self.TARGET_COUNT
        else:
            self.paths = [os.path.join(self.comic_dir, f) for f in selected]
            # on charge grand, c'est `blit_fit` qui fait l'adaptation au rendu
            self.images = [load_image(p, 2000, 2000) for p in self.paths]
            self.names = selected

        # "milieu" de l'histoire basé sur le tri des noms
        self.story_middle_idx = len(self.paths) // 2 if self.paths else None
        self.story_middle_path = self.paths[self.story_middle_idx] if self.paths else None

        # ordre mélangé pour l'affichage
        self.grid_order = list(range(len(self.images)))
        random.shuffle(self.grid_order)

        # état
        self.current_idx = 0
        self.timer = 0.0
        self.state = "moving"   # moving | stopped
        self.result = None
        self.score = 0

        # sons
        self.snd_success = load_sound("success.wav")
        self.snd_fail = load_sound("fail.wav")
        self.snd_click = load_sound("click.wav")

        # pré-calc layout rects (4 haut, 3 bas centré)
        self.tile_rects = self.compute_layout()

    # ---------------- layout & events ----------------
    def compute_layout(self):
        """Layout 4 (haut) + 3 (bas), CENTRÉ horizontalement et verticalement,
        en maximisant la taille sans couper."""
        usable_w = GAME_WIDTH - 2 * self.MARGIN_SIDE
        usable_h = GAME_HEIGHT - self.MARGIN_TOP - self.MARGIN_BOTTOM

        # Taille brute depuis la hauteur (2 rangées + 1 gouttière)
        tile_h = max(60, int((usable_h - self.GUTTER_Y) / 2))
        tile_w = max(60, int(tile_h * self.TILE_ASPECT))

        # Si la rangée du haut (4 tuiles) dépasse en largeur, on réduit
        total_w_top = 4 * tile_w + 3 * self.GUTTER_X
        if total_w_top > usable_w:
            scale = usable_w / total_w_top
            tile_w = max(60, int(tile_w * scale))
            tile_h = max(60, int(tile_w / self.TILE_ASPECT))
            total_w_top = 4 * tile_w + 3 * self.GUTTER_X

        total_w_bot = 3 * tile_w + 2 * self.GUTTER_X  # rangée du bas

        # Centre VERTICALEMENT le bloc 2 rangées
        block_h = 2 * tile_h + self.GUTTER_Y
        top_y = self.MARGIN_TOP + (usable_h - block_h) // 2
        row1_y = top_y + tile_h // 2
        row2_y = row1_y + tile_h + self.GUTTER_Y

        # Centre HORIZONTALLEMENT CHAQUE rangée
        left_top = self.MARGIN_SIDE + (usable_w - total_w_top) // 2 + tile_w // 2
        xs_top = [left_top + i * (tile_w + self.GUTTER_X) for i in range(4)]

        left_bot = self.MARGIN_SIDE + (usable_w - total_w_bot) // 2 + tile_w // 2
        xs_bot = [left_bot + i * (tile_w + self.GUTTER_X) for i in range(3)]

        rects = []
        for x in xs_top:
            rects.append(pygame.Rect(0, 0, tile_w, tile_h).move(x - tile_w // 2, row1_y - tile_h // 2))
        for x in xs_bot:
            rects.append(pygame.Rect(0, 0, tile_w, tile_h).move(x - tile_w // 2, row2_y - tile_h // 2))

        return rects[:len(self.images)]



    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_m, pygame.K_ESCAPE):
                self.game.pop_scene()
            elif e.key == pygame.K_r and self.state == "stopped":
                self.reset()
            elif e.key == pygame.K_SPACE or e.key == pygame.K_RETURN:
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
                # On click after finish, report score and leave
                self.game.complete_minigame(getattr(self, "score", 0), self.result == "win")

    def reset(self):
        self.state = "moving"
        self.result = None
        self.score = 0 
        self.current_idx = 0
        self.timer = 0.0
        random.shuffle(self.grid_order)

    # ---------------- update/draw ----------------
    def update(self, dt):
        if self.state != "moving":
            return
        self.timer += dt
        if self.timer >= 1.0 / self.HIGHLIGHT_SPEED:
            self.timer = 0.0
            total = max(1, len(self.images))
            self.current_idx = (self.current_idx + 1) % total

    def draw_tile(self, screen, rect, img, highlighted):
        # ombre douce
        shadow = rect.move(0, 8)
        srf = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
        pygame.draw.rect(srf, (0, 0, 0, 70), srf.get_rect(), border_radius=16)
        screen.blit(srf, shadow.topleft)

        # fond carte
        card = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card, (30, 34, 44), card.get_rect(), border_radius=16)
        pygame.draw.rect(card, (70, 78, 90), card.get_rect(), 2, border_radius=16)
        screen.blit(card, rect.topleft)

        # image ajustée (avec padding intérieur)
        inner = rect.inflate(-self.TILE_PADDING * 2, -self.TILE_PADDING * 2)
        blit_fit(screen, img, inner)

        # highlight animé (pulse alpha)
        if highlighted:
            pulse = (pygame.time.get_ticks() // 10) % 200
            alpha = 80 + int(60 * abs(100 - pulse) / 100)  # 80..140
            hi = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(hi, (*ACCENT_COLOR[:3], alpha), hi.get_rect(), 6, border_radius=18)
            screen.blit(hi, rect.topleft)

    def validate(self):
        if self.snd_click: self.snd_click.play()
        self.state = "stopped"
        if not self.paths:
            self.result = "lose"
            self.score = 0
            return
        shown_img_idx = self.grid_order[self.current_idx]
        shown_path = self.paths[shown_img_idx]
        middle_idx = self.story_middle_idx  # index de l'image du milieu (4 si 7 images)
        distance = abs(shown_img_idx - middle_idx)
        if distance == 0:
            self.score = 100
            self.result = "win"
            if self.snd_success: self.snd_success.play()
        elif distance == 1:
            self.score = 80
            self.result = "lose"
            if self.snd_fail: self.snd_fail.play()
        elif distance == 2:
            self.score = 60
            self.result = "lose"
            if self.snd_fail: self.snd_fail.play()
        elif distance == 3:
            self.score = 40
            self.result = "lose"
            if self.snd_fail: self.snd_fail.play()
        else:
            self.score = 0
            self.result = "lose"
            if self.snd_fail: self.snd_fail.play()

    def draw(self, screen):
        self.tile_rects = self.compute_layout()
        screen.fill(BG_COLOR)
        blit_text_center(screen, self.title_font.render("Quel est le milieu de l'histoire ?", True, PRIMARY_COLOR), 64)
        blit_text_center(screen, self.ui_font.render("ESPACE/Click pour valider • M: Menu • R: Rejouer", True, SECONDARY_COLOR), 96)
        
        # Draw attempts HUD
        draw_attempts(screen, self.game, pos=(None, 26))

        # dessine les 7 cases suivant l'ordre mélangé
        for grid_idx, rect in enumerate(self.tile_rects):
            img_idx = self.grid_order[grid_idx]
            img = self.images[img_idx]
            self.draw_tile(screen, rect, img, highlighted=(self.state == "moving" and grid_idx == self.current_idx))

        # overlay résultat
        if self.state == "stopped":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            if self.result == "win":
                t1 = self.title_font.render("Bravo ! Tu es bien au milieu de l'histoire", True, GOOD_COLOR)
                t2 = self.ui_font.render("ESPACE/clic pour continuer • R pour rejouer • M pour menu", True, PRIMARY_COLOR)
            else:
                t1 = self.title_font.render("Vous n'êtes pas au milieu de l'histoire !!", True, BAD_COLOR)
                ans = os.path.basename(self.story_middle_path) if self.story_middle_path else "N/A"
                t2 = self.ui_font.render(f"La case du milieu était : {ans}  •  ESPACE/clic pour continuer • R pour rejouer • M pour menu", True, PRIMARY_COLOR)
            blit_text_center(screen, t1, GAME_HEIGHT // 2 - 10)
            blit_text_center(screen, t2, GAME_HEIGHT // 2 + 26)
            
            # Affichage du score
            t3 = self.ui_font.render(f"Score : {self.score}", True, ACCENT_COLOR)
            blit_text_center(screen, t3, GAME_HEIGHT // 2 + 60)