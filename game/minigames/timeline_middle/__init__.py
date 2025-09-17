from ..base import MiniGame, register_minigame
from ...core import Game, Scene
from .scene import TimelineMiddleScene


class TimelineMiddleMiniGame(MiniGame):
    id = "timeline_middle"
    display_name = "Au milieu de l'histoire (iPhone)"

    def create_initial_scene(self, game: Game) -> Scene:
        return TimelineMiddleScene(game)


register_minigame(TimelineMiddleMiniGame())




