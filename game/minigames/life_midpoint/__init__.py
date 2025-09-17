from ..base import MiniGame, register_minigame
from ...core import Game, Scene
from .scene import LifeMidpointScene


class LifeMidpointMiniGame(MiniGame):
    id = "life_midpoint"
    display_name = "Au milieu de la vie"

    def create_initial_scene(self, game: Game) -> Scene:
        return LifeMidpointScene(game)


register_minigame(LifeMidpointMiniGame())




