import os
import pygame
from .config import WIDTH, HEIGHT, SND_DIR, NOT_CENTER_MSG, PRIMARY_COLOR


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def blit_text_center(surface, text_surface, y):
    rect = text_surface.get_rect(center=(WIDTH // 2, y))
    surface.blit(text_surface, rect)


def draw_center_line(surface, x, y, height, color, thickness=3):
    pygame.draw.line(surface, color, (x, y - height // 2), (x, y + height // 2), thickness)


def load_image(path, max_w=720, max_h=400):
    if os.path.isfile(path):
        img = pygame.image.load(path).convert_alpha()
        w, h = img.get_size()
        scale = min(max_w / w, max_h / h, 1.0)
        if scale != 1.0:
            img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
        return img
    else:
        surf = pygame.Surface((max_w, int(max_h * 0.75)), pygame.SRCALPHA)
        surf.fill((40, 44, 52))
        pygame.draw.rect(surf, (70, 80, 90), surf.get_rect(), 3, border_radius=12)
        font = pygame.font.SysFont(None, 28, bold=True)
        txt = font.render("Image manquante", True, (200, 200, 200))
        surf.blit(txt, txt.get_rect(center=surf.get_rect().center))
        return surf


def load_sound(name):
    path = os.path.join(SND_DIR, name)
    if os.path.isfile(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None
    return None


def render_not_center_message(font) -> pygame.Surface:
    """Render the shared 'not center' message with the given font."""
    return font.render(NOT_CENTER_MSG, True, PRIMARY_COLOR)
