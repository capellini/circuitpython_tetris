# pylint: disable=anomalous-backslash-in-string, invalid-name
"""
Let's play some

___________________________________________.___  _________._.
\__    ___/\_   _____/\__    ___/\______   \   |/   _____/| |
  |    |    |    __)_   |    |    |       _/   |\_____  \ | |
  |    |    |        \  |    |    |    |   \   |/        \ \|
  |____|   /_______  /  |____|    |____|_  /___/_______  / __
                   \/                    \/            \/  \/

on the Adafruit PyBadge!

https://learn.adafruit.com/adafruit-pybadge
"""

from game_controls import GameControls
from sound import SoundController
from tetris import Game
from tetris_ui import UserInterface

board_height = 19
board_width = 10

game_controls = GameControls()
game = Game(board_height, board_width, game_controls.keymap)
ui = UserInterface(game)
sc = SoundController()

game.on_state_change += ui.on_game_state_change
game.on_state_change += sc.on_game_state_change
game.on_score_change += ui.update_score
game.on_level_change += ui.update_level

while True:
    event = game_controls.get_event()

    if event:
        game.handle_event(event)

    game.move()
    ui.update()
