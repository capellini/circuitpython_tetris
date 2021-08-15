"""
Logic to represent a game of Tetris.
"""
import random

from util import CallbackProperty, colors

GAME_PIECE_DIMENSION = 4 # game pieces are presented by a 4 x 4 pixel array

class GameState:
    """
    Provide an enum of game states
    """
    @property
    def playing(self):
        """ Represent the playing state as the string "PLAYING" """
        return "PLAYING"

    @property
    def paused(self):
        """ Represent the paused state as the string "PAUSED" """
        return "PAUSED"

    @property
    def gameover(self):
        """ Represent the game over state as the string "GAME OVER" """
        return "GAME OVER"

game_state = GameState()

class GamePiece:
    """
    Class to represent a Tetris piece.  A Tetris piece has an x position,
    a y position, a color, and a rotation

    :param int x: This piece's x position on the field.
    :param int y: This piece's y position on the field.
    """
    x = 0
    y = 0

    game_pieces = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self._game_piece_type = random.randint(0, len(self.game_pieces) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        """
        Get the image representation of this piece.

        :returns tuple An RGB representation fo the color of the piece.
        """
        return self.game_pieces[self._game_piece_type][self.rotation]

    def rotate_left(self):
        """
        Rotate this piece one movement to the left
        """
        self.rotation = (self.rotation - 1) % len(self.game_pieces[self._game_piece_type])

    def rotate_right(self):
        """
        Rotate this piece one movement to the right
        """
        self.rotation = (self.rotation + 1) % len(self.game_pieces[self._game_piece_type])


class Tetris:
    """
    Class to represent the state of the Tetris field.
    """
    field = []

    def __init__(self, height, width):
        self.height = height
        self.width = width

        self.game_piece = None
        self.next_game_piece = None

        self.reset_game()

    def new_game_piece(self):
        """
        Generate a new piece.
        """
        self.game_piece = self.next_game_piece \
            if self.next_game_piece is not None else GamePiece(3, 0)
        self.next_game_piece = GamePiece(3, 0)

    def intersects(self):
        """
        Determine if the current piece is either off the board or hitting the field.
        """
        intersection = False

        for i in range(GAME_PIECE_DIMENSION):
            for j in range(GAME_PIECE_DIMENSION):
                if i * GAME_PIECE_DIMENSION + j in self.game_piece.image():
                    if i + self.game_piece.y > self.height - 1 or \
                       j + self.game_piece.x > self.width - 1 or \
                       j + self.game_piece.x < 0 or \
                       self.field[i + self.game_piece.y][j + self.game_piece.x] > 0:

                        intersection = True

        return intersection

    def clear_full_lines(self):
        """
        Remove lines that are fully-populated by parts of pieces.

        : returns int The number of full lines removed
        """
        line_capacity = tuple(
            sum(int(x > 0) for x in self.field[i]) for i in range(len(self.field))
        )
        full_lines = sum(line_capacity[i] == self.width for i in range(len(line_capacity)))

        # remove full lines and insert new empty lines on top
        self.field = list(
            [0] * self.width for _ in range(full_lines)
        ) + list(self.field[i] for i in range(len(self.field)) if line_capacity[i] < self.width)

        return full_lines

    def move_down(self):
        """
        Move the piece one spot down on the board.
        """
        self.game_piece.y = self.game_piece.y + 1

    def freeze(self):
        """
        Freeze the current piece in place on the field.
        """
        # we've gone down one too many steps, so go up one
        self.game_piece.y -= 1

        image = self.game_piece.image()

        for coord in image:
            x = coord % GAME_PIECE_DIMENSION
            y = coord // GAME_PIECE_DIMENSION

            self.field[y + self.game_piece.y][x + self.game_piece.x] = self.game_piece.color

    def move_laterally(self, dx):
        """
        Move a piece to the side by [dx] units.
        """
        old_x = self.game_piece.x
        self.game_piece.x += dx
        if self.intersects():
            self.game_piece.x = old_x

    def rotate_left(self):
        """
        Rotate a piece to the left.
        """
        old_rotation = self.game_piece.rotation
        self.game_piece.rotate_left()
        if self.intersects():
            self.game_piece.rotation = old_rotation

    def rotate_right(self):
        """
        Rotate a piece to the right.
        """
        old_rotation = self.game_piece.rotation
        self.game_piece.rotate_right()
        if self.intersects():
            self.game_piece.rotation = old_rotation

    def reset_game(self):
        """
        Get ready for a new game by clearing the field and getting a new piece.
        """
        self.field = [[0] * self.width for _ in range(self.height)]
        self.new_game_piece()

class Game:
    """
    Handle top-level aspects of the game, logic of when to move pieces,
    and keep score.
    """
    fps = 1500
    key_fps = 75

    def __init__(self, height, width, keymap):
        self.height = height
        self.width = width

        self.counter = 0
        self.level = 1
        self.score = 0
        self.state = game_state.playing

        self._on_state_change = CallbackProperty()
        self._on_score_change = CallbackProperty()
        self._on_level_change = CallbackProperty()
        self.keymap = keymap
        self.pressed_key = None
        self.tetris = Tetris(self.height, self.width)

    @property
    def on_score_change(self):
        """
        The on_score_change property holds a list of callbacks to call
        when the score changes.
        """
        return self._on_score_change

    @on_score_change.setter
    def on_score_change(self, new):
        if isinstance(new, CallbackProperty):
            self._on_score_change = new

            return

        raise NotImplementedError(
            'Please only use in-place addition and subtraction for callback properties'
        )

    @property
    def on_level_change(self):
        """
        The on_level_change property holds a list of callbacks to call
        when the level changes.
        """
        return self._on_level_change

    @on_level_change.setter
    def on_level_change(self, new):
        if isinstance(new, CallbackProperty):
            self._on_level_change = new

            return

        raise NotImplementedError(
            'Please only use in-place addition and subtraction for callback properties'
        )

    @property
    def on_state_change(self):
        """
        The on_state_change property holds a list of callbacks to call
        when the state changes.
        """
        return self._on_state_change

    @on_state_change.setter
    def on_state_change(self, new):
        if isinstance(new, CallbackProperty):
            self._on_state_change = new

            return

        raise NotImplementedError(
            'Please only use in-place addition and subtraction for callback properties'
        )

    def _change_score(self, score):
        """
        Change the game score and call the appropriate callbacks.
        """
        self.score = score

        level = (self.score // 10) + 1
        if level != self.level:
            self.level = level
            print('Level: {}'.format(level))

            for level_change_callback in self._on_level_change:
                level_change_callback(level)

        for score_change_callback in self.on_score_change:
            score_change_callback(score)

    def _change_state(self, state):
        """
        Change the game state and call the appropriate callbacks.
        """
        self.state = state

        for state_change_callback in self.on_state_change:
            state_change_callback(state)

    def handle_event(self, event):
        """
        Handle a user event by moving the piece on the board.
        """
        if event.pressed:
            # if user wants to rotate, assume they don't press and hold
            if event.key_number == self.keymap.A:
                self.tetris.rotate_left()
            elif event.key_number == self.keymap.B:
                self.tetris.rotate_right()
            elif event.key_number == self.keymap.start:
                self._change_state(
                    game_state.paused
                    if self.state == game_state.playing
                    else game_state.playing
                )
            elif event.key_number == self.keymap.select:
                self.reset_game()
            else: # for directional keys, allow press and hold
                self.pressed_key = event.key_number
        elif event.key_number not in [self.keymap.A, self.keymap.B]:
            self.pressed_key = None

    def check_game_state(self):
        """
        Check if the field needs updating because the active piece has
        fallen onto it, update the field and the score, and make a new
        piece, if needed.  End the game, if needed.
        """
        if self.tetris.intersects():
            self.tetris.freeze()

            full_lines = self.tetris.clear_full_lines()

            if full_lines > 0:
                self._change_score(self.score + full_lines ** 2)

            self.tetris.new_game_piece()

            # if we're intersecting immediately after we generate a new game_piece,
            # then we're at the top of the field, so end the game
            if self.tetris.intersects():
                self._change_state(game_state.gameover)

    def _time_to_move(self, fps):
        """
        Determine if it's time to move the active piece, based upon a
        given frame rate.

        :param fps int the frame rate used to determine if it's time to move a piece.
        """
        return self.counter % fps == 0

    def move(self):
        """
        Move the active piece, if required, and check the game state.
        """
        if self.state in [game_state.paused, game_state.gameover]:
            return

        self.counter += 1
        if self.counter > 100000:
            self.counter = 0

        if self.state == game_state.playing:
            if self._time_to_move(self.fps // self.level) or \
               (self._time_to_move(self.key_fps) and self.pressed_key == self.keymap.down):
                self.tetris.move_down()

            if self.pressed_key is not None and self._time_to_move(self.key_fps):
                if self.pressed_key == self.keymap.left:
                    self.tetris.move_laterally(-1)
                elif self.pressed_key == self.keymap.right:
                    self.tetris.move_laterally(1)

        self.check_game_state()

    def reset_game(self):
        """
        Reset the current game.
        """
        self._change_score(0)
        self._change_state(game_state.playing)
        self.pressed_key = None

        self.tetris.reset_game()
