import random
from .core import Game
from .scenes.menu import MenuScene
from .scenes.center_word import CenterWordScene
from .scenes.session import SessionScene
from .minigames.newton_apple.scene import NewtonAppleScene
from .minigames import get_all_minigames


def create_game_with_menu():
    game = Game()
    menu = MenuScene(game)

    def start_session():
        game.push_scene(SessionScene(game, num_games=5))

    menu.set_menu_items(
        [
            ("Jouer", start_session),
            ("Test Newton", lambda: game.push_scene(NewtonAppleScene(game))),
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
