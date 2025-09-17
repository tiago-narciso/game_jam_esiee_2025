import random
from .core import Game
from .scenes.username import UsernameScene
from .scenes.leaderboard import LeaderboardScene
from .scenes.session import SessionScene
from .minigames.newton_apple.scene import NewtonAppleScene


def create_game():
    game = Game()

    def on_submit(name: str):
        # pop username scene
        game.pop_scene()
        game.push_scene(SessionScene(game, num_games=5, username=name))

    username_scene = UsernameScene(game, on_submit)
    game.push_scene(username_scene)
    return game


def main():
    game = create_game()
    game.run()


if __name__ == "__main__":
    main()
