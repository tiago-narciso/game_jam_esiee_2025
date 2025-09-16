from .base import MiniGame, get_all_minigames, get_minigame_by_id, register_minigame

# Import built-in minigames to ensure registration side-effects
from .center_word import *  # noqa: F401,F403
from .newton_apple import *  # noqa: F401,F403
from .life_midpoint import *  # noqa: F401,F403


