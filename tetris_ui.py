"""
User interface classes.  This module exports a UserInterface class
that can be used to control the display on the board.
"""

import math
import time

# disable import errors on my IDE, since my host is running CPython and not CircuitPython
import analogio  # pylint: disable=import-error
import board  # pylint: disable=import-error
import displayio  # pylint: disable=import-error
import terminalio  # pylint: disable=import-error
import vectorio  # pylint: disable=import-error

from adafruit_display_text import bitmap_label as label  # pylint: disable=import-error

from tetris import game_state, GAME_PIECE_DIMENSION
from util import colors

def initialize_palette(palette_colors):
    """
    Initialize the color palette for game pieces and the game field.
    """
    color_palette = displayio.Palette(len(palette_colors))
    color_palette.make_transparent(0)

    for index, color in enumerate(palette_colors):
        color_palette[index] = color

    return color_palette


palette = initialize_palette(colors)

class GamePiece:
    """
    Represent the active game piece on the board (the one that is
    falling and that you can move around).
    """
    palette = palette

    def __init__(self, field, color, pixel_size):
        piece = displayio.Bitmap(pixel_size, pixel_size, len(self.palette))
        piece.fill(0)

        for fld in field:
            piece[fld % GAME_PIECE_DIMENSION, fld // GAME_PIECE_DIMENSION] = color

        self.grid = displayio.TileGrid(
            piece, pixel_shader=self.palette, width=1, height=1,
            tile_width=pixel_size, tile_height=pixel_size
        )

    def update(self, x, y):
        """
        Update the position of this game piece on the board.

        :param float x position on the board
        :param float y y position on the board
        """
        self.grid.x = x
        self.grid.y = y

class GameField:
    """
    Represent the field of pieces which have already fallen to the bottom.
    """
    palette = palette

    def __init__(self, game_field):
        width = len(game_field[0])
        height = len(game_field)

        field = displayio.Bitmap(width, height, len(self.palette))

        for x in range(width):
            for y in range(height):
                field[x, y] = game_field[y][x]

        self.grid = displayio.TileGrid(
            field, pixel_shader=self.palette, width=1, height=1,
            tile_width=width, tile_height=height
        )

class GameBoard:
    """
    Display the Tetris game (board background, field, game piece, etc).
    """
    screen = displayio.Group()

    def __init__(self, display, screen, game):
        self.display = display
        self.game = game.tetris

        self.square_size = math.floor(board.DISPLAY.height / self.game.height)
        self.game_piece = None
        self.game_piece_image = None
        self.piece = None
        self.field = None

        self.screen4x = displayio.Group(scale=self.square_size)
        screen.append(self.screen)
        screen.append(self.screen4x)


    def create_game_border(self, board_palette):
        """
        Draw the outline for the entire game board.

        :param board_palette ~displayio.Palette Palette for drawing the game board.
        """
        width = self.square_size * self.game.width + 1
        height = self.square_size * self.game.height + 1

        square = displayio.Bitmap(width, height, 2)
        square.fill(0)

        for w in range(width):
            for h in range(height):
                if w == 0 or h == 0 or width - 1 == w or height - 1 == h:
                    square[w, h] = 1

        square_grid = displayio.TileGrid(
            square, pixel_shader=board_palette, width=1, height=1,
            tile_width=width, tile_height=height
        )

        return square_grid

    def create_game_board_squares(self, board_palette):
        """
        Draw the grid of squares on the game board.

        :param board_palette ~displayio.Palette Palette for drawing the game board.
        """
        square = displayio.Bitmap(self.square_size, self.square_size, 2)
        square.fill(0)

        for i in range(self.square_size):
            for j in range(self.square_size):
                if i == 0 or j == 0:
                    square[i, j] = 1

        square_grid = displayio.TileGrid(
            square, pixel_shader=board_palette, width=self.game.width, height=self.game.height,
            tile_width=self.square_size, tile_height=self.square_size
        )

        return square_grid

    def draw_board(self):
        """
        Draw the background for the game board.
        """
        board_palette = displayio.Palette(2)
        board_palette[0] = (200, 200, 200)
        board_palette[1] = (50, 50, 50)

        self.screen.append(self.create_game_border(board_palette))
        self.screen.append(self.create_game_board_squares(board_palette))

    def update(self):
        """
        Update the game board display.
        """
        game_piece = self.game.game_piece

        if self.game_piece != game_piece or self.game_piece_image != game_piece.image():
            if self.piece is not None:
                self.screen4x.remove(self.piece.grid)

            self.game_piece = game_piece
            self.game_piece_image = game_piece.image()
            self.piece = GamePiece(game_piece.image(), game_piece.color, self.square_size)

            self.screen4x.append(self.piece.grid)

            if self.field is not None:
                self.screen4x.remove(self.field.grid)

            self.field = GameField(self.game.field)

            self.screen4x.append(self.field.grid)

        self.piece.update(self.game_piece.x, self.game_piece.y)


def create_game_over_palette():
    """ Create the color palette for the game over modal """
    game_over_palette = displayio.Palette(1)
    game_over_palette[0] = (200, 200, 200)

    return game_over_palette

class GameOver:
    """
    Class to represent the game over modal.

    :param model displayio.Group The modal group to attach to the display.
    """
    def __init__(self):
        self.modal = displayio.Group(x=5, y=30)

        go_label = label.Label(
            font=terminalio.FONT, x=20, y=25, color=0x0, scale=2, text="Game Over"
        )
        select_label = label.Label(
            font=terminalio.FONT, x=12, y=50, color=0x0, text="Select to play again"
        )
        background = vectorio.Rectangle(
            pixel_shader=create_game_over_palette(), height=70, width=150
        )

        self.modal.append(background)
        self.modal.append(go_label)
        self.modal.append(select_label)

class BatteryLevelIndicator:
    """
    Display the battery level on the screen.
    """
    # I have no idea if I'm doing this right
    adc = analogio.AnalogIn(board.A6)

    # SWAGs from some observation
    max_level = 38000
    min_level = 31000

    group = displayio.Group()
    battery_level_label = label.Label(
        font=terminalio.FONT, x=70, y=board.DISPLAY.height - 20, color=0x999999, text="Battery:"
    )
    battery_level_text = label.Label(
        font=terminalio.FONT, x=120, y=board.DISPLAY.height - 20, color=0x999999
    )

    def __init__(self):
        self.group.append(self.battery_level_label)
        self.group.append(self.battery_level_text)
        self.last_check = 0

        self.battery_level = self.adc.value
        self.battery_level_percent = self.calculate_battery_level(self.battery_level)
        self.battery_level_text.text = '{}%'.format(self.battery_level_percent)

    @property
    def battery_level_percent(self):
        """ Expose the battery level in percentage form """
        return self._battery_level_percent

    @battery_level_percent.setter
    def battery_level_percent(self, value):
        """
        Set the battery level percent and change the text color, if necessary, to
        indicate a low battery state.
        """
        int_value = int(value)

        if int_value < 25:
            color = 0xff0000
        elif 25 <= int_value < 50:
            color = 0xffff00
        else:
            color = 0x999999

        self.battery_level_label.color = color
        self.battery_level_text.color = color
        self._battery_level_percent = value

    def calculate_battery_level(self, value):
        """
        Calculate the battery level to the nearest 5%.
        """
        level = math.floor(min(
            max(value - self.min_level, 0) / (self.max_level - self.min_level), 1
        ) * 100)

        return 5 * round(level / 5)

    def update(self):
        """
        Calculate the battery level and update the display if it has changed by +/-5% or greater.
        """
        if time.monotonic() - self.last_check > 60:
            self.last_check = time.monotonic()
            current_level = self.adc.value
            average_level = (self.battery_level * 4 + current_level) / 5

            self.battery_level = average_level
            battery_level_percent = self.calculate_battery_level(self.battery_level)

            if battery_level_percent != self.battery_level_percent:
                self.battery_level_percent = battery_level_percent
                self.battery_level_text.text = '{}%'.format(self.battery_level_percent)

    def __del__(self):
        self.adc.deinit()

class NextPiecePreview:
    """
    A widget to show the next piece that will be used on the board.

    :param group displayio.Group The group containing all widget elements
    """
    label = label.Label(font=terminalio.FONT, x=0, y=0, color=0x999999, text="Next Piece:")

    def __init__(self, game):
        self.game = game.tetris
        self.scale = math.floor(board.DISPLAY.height / self.game.height)
        self.piece_group = displayio.Group(scale=self.scale, x=20, y=15)
        self.group = displayio.Group(x=70, y=50)
        self.group.append(self.label)
        self.group.append(self.piece_group)

        self.game_piece = None
        self.game_piece_image = None

        self.update()

    def update(self):
        """
        Update the display to show the next piece, if required.
        """
        game_piece = self.game.next_game_piece

        if self.game_piece != game_piece or self.game_piece_image != game_piece.image():
            if len(self.piece_group) > 0:
                self.piece_group.pop()

            self.game_piece = game_piece
            self.game_piece_image = game_piece.image()

            piece = GamePiece(game_piece.image(), game_piece.color, self.scale)

            self.piece_group.append(piece.grid)

class UserInterface:
    """
    Represents the display's user interface, handling drawing the board, score card, etc.
    """
    display = board.DISPLAY

    top_screen = displayio.Group()
    score_label_label = label.Label(font=terminalio.FONT, x=70, y=5, color=0xcccccc, text="Score:")
    score_label = label.Label(font=terminalio.FONT, x=105, y=5, color=0xcccccc, text="000")

    level_group = displayio.Group()
    level_label_label = label.Label(font=terminalio.FONT, x=70, y=20, color=0x999999, text="Level:")
    level_label = label.Label(font=terminalio.FONT, x=105, y=20, color=0x999999, text="01")

    def __init__(self, game):
        self.display.auto_refresh = False  # only update display on display.refresh()

        self.game_board = GameBoard(self.display, self.top_screen, game)
        self.game_board.draw_board()

        self.game_over = GameOver()

        self.top_screen.append(self.score_label_label)
        self.top_screen.append(self.score_label)

        self.level_group.append(self.level_label_label)
        self.level_group.append(self.level_label)
        self.top_screen.append(self.level_group)

        self.battery_level = BatteryLevelIndicator()
        self.top_screen.append(self.battery_level.group)

        self.next_piece_preview = NextPiecePreview(game)
        self.top_screen.append(self.next_piece_preview.group)

        self.display.show(self.top_screen)

        self.is_paused = False
        self.game_is_over = False

    def update(self):
        """
        Update the game board.
        """
        if not (self.is_paused or self.game_is_over):
            self.game_board.update()
            self.next_piece_preview.update()

        self.battery_level.update()

        self.display.refresh()

    def on_game_state_change(self, state):
        """
        React to the game state changing
        """
        if state == game_state.gameover and not self.game_is_over:
            self.show_game_over()
            self.game_is_over = True
        elif state != game_state.gameover and self.game_is_over:
            self.hide_game_over()
            self.game_is_over = False

        self.is_paused = state == game_state.paused

    def update_score(self, score):
        """
        Update the score on the display.  Callback passed into the
        game instance that is called whenever the score is updated.
        """
        self.score_label.text = ("%03d" % score)

    def update_level(self, level):
        """
        Update the score on the display.  Callback passed into the
        game instance that is called whenever the score is updated.
        """
        self.level_label.text = ("%02d" % level)

    def hide_game_over(self):
        """ Hide the game over modal """
        self.top_screen.pop()

    def show_game_over(self):
        """
        Display to the user that the game is over
        """
        self.top_screen.append(self.game_over.modal)
