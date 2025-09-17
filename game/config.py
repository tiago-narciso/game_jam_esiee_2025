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
FONT_DIR = os.path.join(ASSETS_DIR, "fonts")
FONT_PATH = os.path.join(FONT_DIR, "VCR_OSD_MONO.ttf")

# Shared messages
NOT_CENTER_MSG = "Vous n'êtes pas au centre du jeu."



# Minigame: Life Midpoint dataset (name, birth_year, death_year)
CELEBRITIES = [
    ("Marie Curie", 1867, 1934),
    ("Isaac Newton", 1643, 1727),
    ("Albert Einstein", 1879, 1955),
    ("Léonard de Vinci", 1452, 1519),
    ("Napoléon Bonaparte", 1769, 1821),
    ("Cléopâtre", -69, -30),
    ("Molière", 1622, 1673),
    ("Victor Hugo", 1802, 1885),
]

# Life Midpoint minigame settings
LIFE_KEY_SPEED = 220  # pixels per second left/right
LIFE_TIMELINE_PADDING_YEARS = 20  # extra years before birth and after death
LIFE_TARGET_KIND = "random"  # "random" or "midpoint" (for fallback/testing)

