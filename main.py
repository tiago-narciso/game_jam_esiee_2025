import arcade
import sys
import traceback

# --- Config ---
WIDTH, HEIGHT = 900, 360
TITLE = "Au Centre de l'Histoire — Arcade (fix 3.x)"
WORD = "HISTOIRE"
TOLERANCE_PX = 8
CURSOR_SPEED = 300  # px/s

BG = (20, 24, 30)
WHITE = (240, 240, 240)
ACCENT = (120, 200, 255)
GOOD = (120, 220, 160)
BAD = (250, 110, 110)
LINE = (80, 90, 110)
CENTER_HINT = (90, 160, 210)

class CenterGame(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE, resizable=False)
        arcade.set_background_color(BG)
        # Taux d'update si dispo
        try:
            self.set_update_rate(1/120)
        except Exception:
            pass

        self.cursor_x = WIDTH // 2
        self.left_pressed = False
        self.right_pressed = False
        self.result = None   # None | "win" | "lose"
        self.error_px = None

        self.true_center_x = WIDTH // 2
        self.word_y = HEIGHT // 2 + 30
        self.line_y = self.word_y - 70

        self.title_size = 34
        self.word_size = 140
        self.ui_size = 18

    def on_draw(self):
        # ✅ Arcade 3.x : on utilise clear() au lieu de start_render()
        self.clear()

        # En-tête
        arcade.draw_text("Au Centre de l'Histoire", 20, HEIGHT - 50, WHITE, self.title_size)
        arcade.draw_text("Placez le curseur au CENTRE du mot, puis ESPACE pour valider.",
                         20, HEIGHT - 78, (200, 200, 200), self.ui_size)

        # Mot centré
        arcade.draw_text(WORD, WIDTH/2, self.word_y, WHITE, self.word_size, anchor_x="center")

        # Ligne de référence
        arcade.draw_line(60, self.line_y, WIDTH - 60, self.line_y, LINE, 2)

        # Repère du centre réel
        arcade.draw_line(self.true_center_x, self.line_y - 28, self.true_center_x, self.line_y + 28, CENTER_HINT, 1)

        # Curseur joueur
        color = ACCENT if self.result is None else (GOOD if self.result == "win" else BAD)
        arcade.draw_line(self.cursor_x, self.line_y - 36, self.cursor_x, self.line_y + 36, color, 3)
        arcade.draw_circle_filled(self.cursor_x, self.line_y, 5, color)

        # HUD précision
        diff = abs(self.cursor_x - self.true_center_x)
        hud = f"Décalage: {int(diff)} px (Tolérance: {TOLERANCE_PX}px)"
        arcade.draw_text(hud, 20, 18, (210, 210, 210), self.ui_size)

        # Résultat
        if self.result is not None:
            arcade.draw_lrbt_rectangle_filled(0, WIDTH, 0, HEIGHT, (0, 0, 0, 150))
            if self.result == "win":
                title = "Parfait ! Vous êtes au centre de l'histoire."
                detail = f"Erreur: {int(self.error_px)} px (≤ {TOLERANCE_PX}px)"
                col = GOOD
            else:
                title = "Perdu : Vous n'êtes pas au centre de l'histoire."
                detail = f"Erreur: {int(self.error_px)} px (> {TOLERANCE_PX}px)"
                col = BAD

            arcade.draw_text(title, WIDTH/2, HEIGHT/2 + 16, col, 26, anchor_x="center")
            arcade.draw_text(detail, WIDTH/2, HEIGHT/2 - 8, WHITE, 16, anchor_x="center")
            arcade.draw_text("Appuyez sur R pour rejouer • ÉCHAP pour quitter",
                             WIDTH/2, HEIGHT/2 - 34, (220, 220, 220), 14, anchor_x="center")

    def on_update(self, delta_time: float):
        if self.result is None:
            dx = 0
            if self.left_pressed:
                dx -= CURSOR_SPEED * delta_time
            if self.right_pressed:
                dx += CURSOR_SPEED * delta_time
            if dx != 0:
                self.cursor_x = max(0, min(WIDTH, self.cursor_x + dx))

    # Clavier
    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.close()
        elif symbol == arcade.key.LEFT:
            self.left_pressed = True
        elif symbol == arcade.key.RIGHT:
            self.right_pressed = True
        elif symbol == arcade.key.SPACE and self.result is None:
            self.validate()
        elif symbol == arcade.key.R and self.result is not None:
            self.reset()

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.left_pressed = False
        elif symbol == arcade.key.RIGHT:
            self.right_pressed = False

    # Souris
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.result is None:
            self.cursor_x = max(0, min(WIDTH, x))

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.result is None:
            self.cursor_x = max(0, min(WIDTH, x))

    # Logique
    def validate(self):
        self.error_px = abs(self.cursor_x - self.true_center_x)
        self.result = "win" if self.error_px <= TOLERANCE_PX else "lose"

    def reset(self):
        self.cursor_x = WIDTH // 2
        self.left_pressed = False
        self.right_pressed = False
        self.result = None
        self.error_px = None

def main():
    try:
        CenterGame()
        arcade.run()
    except Exception:
        traceback.print_exc()
        input("\nUne erreur est survenue. Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()
