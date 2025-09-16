from ..base import MiniGame, register_minigame
from ...core import Game, Scene
from .scene import NewtonAppleScene


class NewtonAppleMiniGame(MiniGame):
    id = "newton_apple"
    display_name = "La pomme de Newton"

    def create_initial_scene(self, game: Game) -> Scene:
        return NewtonAppleScene(game)


register_minigame(NewtonAppleMiniGame())


