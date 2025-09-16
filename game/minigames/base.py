from typing import Callable, Dict, List, Optional
from ..core import Game, Scene


class MiniGame:
    """Abstract minigame: returns an initial Scene to be pushed.

    Each minigame is free to manage its own internal scenes and inputs.
    """

    id: str
    display_name: str

    def create_initial_scene(self, game: Game) -> Scene:
        raise NotImplementedError


_REGISTRY: Dict[str, MiniGame] = {}


def register_minigame(minigame: MiniGame) -> None:
    _REGISTRY[minigame.id] = minigame


def get_minigame_by_id(minigame_id: str) -> Optional[MiniGame]:
    return _REGISTRY.get(minigame_id)


def get_all_minigames() -> List[MiniGame]:
    return list(_REGISTRY.values())



