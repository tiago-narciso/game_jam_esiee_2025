from ..base import MiniGame, register_minigame
from ...core import Game, Scene
from .scene import CenterWordScene


class CenterWordMiniGame(MiniGame):
    id = "center_word"
    display_name = "Au centre du mot"

    def create_initial_scene(self, game: Game) -> Scene:
        return CenterWordScene(game)


register_minigame(CenterWordMiniGame())



