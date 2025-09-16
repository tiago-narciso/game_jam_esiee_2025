from .base import MiniGame, get_all_minigames, get_minigame_by_id, register_minigame

# Import built-in minigames to ensure registration side-effects
from . import center_word  # noqa: F401
from . import newton_apple  # noqa: F401
