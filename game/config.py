import os


# ------------------ Global Config ------------------
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

# Assets
ASSETS_DIR = os.path.join("assets")
IMG_DIR = os.path.join(ASSETS_DIR, "images")
SND_DIR = os.path.join(ASSETS_DIR, "sounds")

# Shared messages
NOT_CENTER_MSG = "Vous n'êtes pas au centre du jeu."
