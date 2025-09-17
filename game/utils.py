import os
import pygame
from .config import WIDTH, HEIGHT, SND_DIR, NOT_CENTER_MSG, PRIMARY_COLOR, SECONDARY_COLOR, GOOD_COLOR, BAD_COLOR


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


def draw_80s_computer_frame(surface: pygame.Surface) -> None:
    """Draw an 80s computer monitor frame around the game surface.
    
    Features:
    - Gray plastic bezel with rounded corners
    - Thicker bottom section (chin) with power LED
    - Screen area remains transparent for gameplay
    - Retro computer aesthetic
    """
    width, height = surface.get_size()
    
    # Create overlay surface for the frame
    frame = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Gray plastic colors
    dark_gray = (60, 60, 65, 255)      # Main bezel
    medium_gray = (80, 80, 85, 255)    # Inner accent
    light_gray = (100, 100, 105, 255)  # Highlight
    very_dark = (40, 40, 45, 255)      # Shadow
    
    # Main bezel frame (outer border)
    bezel_thickness = 24
    outer_rect = pygame.Rect(0, 0, width, height)
    inner_rect = outer_rect.inflate(-bezel_thickness * 2, -bezel_thickness * 2)
    
    # Draw main bezel (only border, not filled)
    pygame.draw.rect(frame, dark_gray, outer_rect, width=bezel_thickness, border_radius=20)
    
    # Inner accent line
    pygame.draw.rect(frame, medium_gray, inner_rect, width=6, border_radius=0)
    
    # Highlight on top edge for 3D effect
    highlight_rect = pygame.Rect(bezel_thickness, bezel_thickness, 
                                width - bezel_thickness * 2, 8)
    pygame.draw.rect(frame, light_gray, highlight_rect, border_radius=4)
    
    # Bottom chin section (thicker area)
    chin_height = 50
    chin_rect = pygame.Rect(bezel_thickness, height - chin_height - bezel_thickness,
                           width - bezel_thickness * 2, chin_height)
    
    # Chin panel
    pygame.draw.rect(frame, dark_gray, chin_rect, border_radius=0)
    pygame.draw.rect(frame, medium_gray, chin_rect.inflate(-8, -8), width=3, border_radius=8)
    
    # Power LED (green dot on left side)
    led_x = chin_rect.left + 30
    led_y = chin_rect.centery
    pygame.draw.circle(frame, (0, 255, 0, 200), (led_x, led_y), 4)
    pygame.draw.circle(frame, (255, 255, 255, 100), (led_x, led_y), 2)
    
    # Power LED label
    font = pygame.font.SysFont(None, 16)
    led_text = font.render("PWR", True, (200, 200, 200, 180))
    frame.blit(led_text, (led_x - 15, led_y + 8))
    
    # Speaker grille (right side)
    grille_x = chin_rect.right - 80
    grille_y = chin_rect.centery - 10
    for i in range(8):
        x = grille_x + i * 8
        pygame.draw.rect(frame, (70, 70, 75, 150), 
                        pygame.Rect(x, grille_y, 4, 20), border_radius=2)
    
    # Brand/model text area (center)
    brand_rect = pygame.Rect(0, 0, 120, 20)
    brand_rect.center = (chin_rect.centerx, chin_rect.centery)
    pygame.draw.rect(frame, (50, 50, 55, 180), brand_rect, border_radius=4)
    
    # Model text
    model_font = pygame.font.SysFont(None, 14, bold=True)
    model_text = model_font.render("GAME JAM 2025", True, (180, 180, 180, 200))
    text_rect = model_text.get_rect(center=brand_rect.center)
    frame.blit(model_text, text_rect)
    
    # Corner screws (decorative)
    screw_color = (120, 120, 125, 200)
    screw_positions = [
        # (bezel_thickness + 10, bezel_thickness + 10),
        # (width - bezel_thickness - 10, bezel_thickness + 10),
        (bezel_thickness + 10, height - bezel_thickness - 10),
        (width - bezel_thickness - 10, height - bezel_thickness - 10)
    ]
    
    for pos in screw_positions:
        pygame.draw.circle(frame, screw_color, pos, 3)
        pygame.draw.circle(frame, (160, 160, 165, 150), pos, 1)
    
    # Apply the frame to the surface
    surface.blit(frame, (0, 0))


def draw_attempts(surface, game, pos=(None, 24)):
    """Draw attempts HUD as small circles. pos: (x, y); x=None → right margin."""
    if getattr(game, "max_attempts_per_game", None) is None:
        return
    max_att = int(game.max_attempts_per_game)
    left = int(game.current_attempts_left) if game.current_attempts_left is not None else max_att
    y = pos[1] if pos[1] is not None else 24
    radius = 8
    gap = 8
    total_w = max_att * (radius * 2) + (max_att - 1) * gap
    x0 = WIDTH - 20 - total_w if pos[0] is None else pos[0]
    for i in range(max_att):
        cx = x0 + i * (radius * 2 + gap) + radius
        color = GOOD_COLOR if i < left else (90, 90, 90)
        pygame.draw.circle(surface, color, (cx, y), radius)
        pygame.draw.circle(surface, (30, 30, 30), (cx, y), radius, 2)
