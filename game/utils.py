import os
import pygame
from .config import WIDTH, HEIGHT, SND_DIR, FONT_PATH, NOT_CENTER_MSG, WIN_MSG, PRIMARY_COLOR, SECONDARY_COLOR, GOOD_COLOR, BAD_COLOR, FRAME_BEZEL_THICKNESS, FRAME_CHIN_HEIGHT, GAME_WIDTH, GAME_HEIGHT


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def blit_text_center(surface, text_surface, y):
    rect = text_surface.get_rect(center=(GAME_WIDTH // 2, y))
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
        font = pygame.font.Font(FONT_PATH, 28)
        txt = font.render("Image manquante", True, (200, 200, 200))
        surf.blit(txt, txt.get_rect(center=surf.get_rect().center))
        return surf


_SOUND_CACHE = {}
_SOUND_ALIASES = {
    # Logical → actual filenames present in assets/sounds
    "success.wav": "success_bell-6776.wav",
    "fail.wav": "error-08-206492.wav",
    "click.wav": None,  # no dedicated click provided; stays None
    "sarcastic.wav": "sarcastic-clapping-sound-186117.wav",
    "lofi.wav": "lo-fi-alarm-clock-243766.wav",
}

_DEFAULT_VOLUME = {
    # Lower SFX a bit; keep music moderate
    "success.wav":  1.00,
    "fail.wav": 0.28,
    "click.wav": 0.18,
    "sarcastic.wav": 0.5,
    # music volume handled via mixer.music in core
}


def _resolve_sound_filename(name: str) -> str | None:
    actual = _SOUND_ALIASES.get(name, name)
    return actual


def load_sound(name):
    if name in _SOUND_CACHE:
        return _SOUND_CACHE[name]
    actual_name = _resolve_sound_filename(name)
    if not actual_name:
        _SOUND_CACHE[name] = None
        return None
    path = os.path.join(SND_DIR, actual_name)
    if os.path.isfile(path):
        try:
            snd = pygame.mixer.Sound(path)
            vol = _DEFAULT_VOLUME.get(name)
            if isinstance(vol, (int, float)):
                try:
                    snd.set_volume(max(0.0, min(1.0, float(vol))))
                except Exception:
                    pass
            _SOUND_CACHE[name] = snd
            return snd
        except Exception:
            _SOUND_CACHE[name] = None
            return None
    _SOUND_CACHE[name] = None
    return None


def get_music_path(name: str) -> str | None:
    actual_name = _resolve_sound_filename(name)
    if not actual_name:
        return None
    path = os.path.join(SND_DIR, actual_name)
    return path if os.path.isfile(path) else None


def render_not_center_message(font) -> pygame.Surface:
    """Render the shared 'not center' message with the given font in error color."""
    return font.render(NOT_CENTER_MSG, True, BAD_COLOR)


def render_win_message(font) -> pygame.Surface:
    """Render the shared win message with the given font in success color."""
    return font.render(WIN_MSG, True, GOOD_COLOR)


def get_game_area_rect() -> pygame.Rect:
    """Get the rectangle where game content should be drawn (inside the frame)."""
    return pygame.Rect(FRAME_BEZEL_THICKNESS, FRAME_BEZEL_THICKNESS, GAME_WIDTH, GAME_HEIGHT)


def draw_80s_computer_frame(surface: pygame.Surface) -> None:
    """Draw an 80s computer monitor frame around the game surface.
    
    Features:
    - Gray plastic bezel with rounded corners
    - Thicker bottom section (chin) with power LED
    - Screen area remains transparent for gameplay
    - Retro computer aesthetic
    """
    width, height = surface.get_size()
    
    # Gray plastic colors
    dark_gray = (60, 60, 65)      # Main bezel
    medium_gray = (80, 80, 85)    # Inner accent
    light_gray = (100, 100, 105)  # Highlight
    
    # Main bezel frame (outer border)
    outer_rect = pygame.Rect(0, 0, width, height)
    inner_rect = outer_rect.inflate(-FRAME_BEZEL_THICKNESS * 2, -FRAME_BEZEL_THICKNESS * 2)
    
    # Fill the entire surface with dark gray (bezel color)
    surface.fill(dark_gray)
    
    # Clear the center area for the game (make it black)
    pygame.draw.rect(surface, (0, 0, 0), inner_rect)
    
    # Inner accent line
    pygame.draw.rect(surface, medium_gray, inner_rect, width=6, border_radius=0)
    
    # Highlight on top edge for 3D effect
    highlight_rect = pygame.Rect(FRAME_BEZEL_THICKNESS, FRAME_BEZEL_THICKNESS, 
                                width - FRAME_BEZEL_THICKNESS * 2, 8)
    pygame.draw.rect(surface, light_gray, highlight_rect, border_radius=4)
    
    # Bottom chin section (thicker area)
    chin_rect = pygame.Rect(FRAME_BEZEL_THICKNESS, height - FRAME_CHIN_HEIGHT - FRAME_BEZEL_THICKNESS,
                           width - FRAME_BEZEL_THICKNESS * 2, FRAME_CHIN_HEIGHT)
    
    # Chin panel
    pygame.draw.rect(surface, dark_gray, chin_rect, border_radius=0)
    pygame.draw.rect(surface, medium_gray, chin_rect.inflate(-8, -8), width=3, border_radius=8)
    
    # Power LED (green dot on left side)
    led_x = chin_rect.left + 30
    led_y = chin_rect.centery
    pygame.draw.circle(surface, (0, 255, 0), (led_x, led_y), 4)
    pygame.draw.circle(surface, (255, 255, 255), (led_x, led_y), 2)
    
    # Power LED label
    font = pygame.font.Font(FONT_PATH, 16)
    led_text = font.render("PWR", True, (200, 200, 200))
    surface.blit(led_text, (led_x - 15, led_y + 8))
    
    # Speaker grille (right side)
    grille_x = chin_rect.right - 80
    grille_y = chin_rect.centery - 10
    for i in range(8):
        x = grille_x + i * 8
        pygame.draw.rect(surface, (70, 70, 75), 
                        pygame.Rect(x, grille_y, 4, 20), border_radius=2)
    
    # Brand/model text area (center)
    brand_rect = pygame.Rect(0, 0, 120, 20)
    brand_rect.center = (chin_rect.centerx, chin_rect.centery)
    pygame.draw.rect(surface, (50, 50, 55), brand_rect, border_radius=4)
    
    # Model text
    model_font = pygame.font.Font(FONT_PATH, 14)
    model_text = model_font.render("AU MILIEU", True, (180, 180, 180))
    text_rect = model_text.get_rect(center=brand_rect.center)
    surface.blit(model_text, text_rect)
    
    # Corner screws (decorative)
    screw_color = (120, 120, 125)
    screw_positions = [
        (FRAME_BEZEL_THICKNESS + 10, height - FRAME_BEZEL_THICKNESS - 10),
        (width - FRAME_BEZEL_THICKNESS - 10, height - FRAME_BEZEL_THICKNESS - 10)
    ]
    
    for pos in screw_positions:
        pygame.draw.circle(surface, screw_color, pos, 3)
        pygame.draw.circle(surface, (160, 160, 165), pos, 1)


def create_scanlines(width, height, line_height=2, alpha=30):
    """Create a surface with a scanline effect."""
    scanline_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, line_height * 2):
        pygame.draw.rect(scanline_surface, (0, 0, 0, alpha), (0, y, width, line_height))
    return scanline_surface


def crt_shutdown_effect(screen, duration, game_surface, game_area):
    """Simulate a CRT screen shutting down."""
    snapshot = game_surface.copy()
    
    # Shrink and brighten effect
    for i in range(100, 0, -5):
        height = int(game_area.height * (i / 100.0))
        if height <= 0:
            break
        
        scaled = pygame.transform.scale(snapshot, (game_area.width, height))
        
        # Redraw the full frame
        frame_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_80s_computer_frame(frame_surface)
        
        # Blit the shrinking image
        y = game_area.centery - height // 2
        frame_surface.blit(scaled, (game_area.left, y))
        
        # Scale and draw to screen
        screen.blit(pygame.transform.scale(frame_surface, screen.get_rect().size), (0, 0))
        pygame.display.flip()
        pygame.time.delay(duration // 20)

    # Final white line
    frame_surface = pygame.Surface((WIDTH, HEIGHT))
    draw_80s_computer_frame(frame_surface)
    pygame.draw.line(frame_surface, (255, 255, 255), (game_area.left, game_area.centery), (game_area.right, game_area.centery), 4)
    screen.blit(pygame.transform.scale(frame_surface, screen.get_rect().size), (0, 0))
    pygame.display.flip()
    pygame.time.delay(200)


def crt_power_on_effect(screen, duration, final_surface, game_area):
    """Simulate a CRT screen powering on."""
    # Start with a white line
    frame_surface = pygame.Surface((WIDTH, HEIGHT))
    draw_80s_computer_frame(frame_surface)
    pygame.draw.line(frame_surface, (255, 255, 255), (game_area.left, game_area.centery), (game_area.right, game_area.centery), 4)
    screen.blit(pygame.transform.scale(frame_surface, screen.get_rect().size), (0, 0))
    pygame.display.flip()
    pygame.time.delay(200)

    # Expand and fade in effect
    for i in range(0, 101, 5):
        height = int(game_area.height * (i / 100.0))
        if height <= 0:
            continue
        
        scaled = pygame.transform.scale(final_surface, (game_area.width, height))
        
        # Redraw the full frame
        frame_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_80s_computer_frame(frame_surface)
        
        # Blit the expanding image
        y = game_area.centery - height // 2
        frame_surface.blit(scaled, (game_area.left, y))
        
        # Scale and draw to screen
        screen.blit(pygame.transform.scale(frame_surface, screen.get_rect().size), (0, 0))
        pygame.display.flip()
        pygame.time.delay(duration // 20)


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
    x0 = GAME_WIDTH - 20 - total_w if pos[0] is None else pos[0]
    for i in range(max_att):
        cx = x0 + i * (radius * 2 + gap) + radius
        color = GOOD_COLOR if i < left else (90, 90, 90)
        pygame.draw.circle(surface, color, (cx, y), radius)
        pygame.draw.circle(surface, (30, 30, 30), (cx, y), radius, 2)
