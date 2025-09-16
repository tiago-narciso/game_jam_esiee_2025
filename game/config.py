import os


# ------------------ Global Config ------------------
WIDTH, HEIGHT = 960, 540
FPS = 120
TITLE = "Game Jam 2025 – Vous n'êtes pas au centre de l'histoire (Pygame)"

# Colors
WHITE = (240, 240, 240)
GRAY = (120, 130, 140)
DARK = (20, 24, 30)
ACCENT = (120, 200, 255)
GOOD = (120, 220, 160)
BAD = (250, 110, 110)

# Assets
ASSETS_DIR = os.path.join("assets")
IMG_DIR = os.path.join(ASSETS_DIR, "images")
SND_DIR = os.path.join(ASSETS_DIR, "sounds")

# Shared messages
NOT_CENTER_MSG = "Vous n'êtes pas au centre du jeu."



