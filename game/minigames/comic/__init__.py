from ..base import MiniGame, register_minigame
from ...core import Game, Scene
from .scene import ComicScene


class ComicMiniGame(MiniGame):
    id = "comic"
    display_name = "BD – Trouver le milieu"

    def create_initial_scene(self, game: Game) -> Scene:
        return ComicScene(game)


register_minigame(ComicMiniGame())




