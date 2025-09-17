import random
from .core import Game
from .scenes.menu import MenuScene
from .scenes.username import UsernameScene
from .scenes.leaderboard import LeaderboardScene
from .scenes.session import SessionScene
from .minigames.newton_apple.scene import NewtonAppleScene
from .minigames.comic.scene import ComicScene
from .minigames import get_all_minigames


def create_game_with_menu():
    game = Game()
    menu = MenuScene(game)

    def start_session():
        def on_submit(name: str):
            # pop username scene
            game.pop_scene()
            game.push_scene(SessionScene(game, num_games=5, username=name))
        game.push_scene(UsernameScene(game, on_submit))

    menu.set_menu_items(
        [
            ("Jouer", start_session),
            ("Test BD", lambda: game.push_scene(ComicScene(game))),
            ("Leaderboard (à venir)", lambda: None),
            ("Quitter", lambda: game.quit()),
        ]
    )
    game.push_scene(menu)
    return game


def main():
    game = create_game_with_menu()
    game.run()


if __name__ == "__main__":
    main()
