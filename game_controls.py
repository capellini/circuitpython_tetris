"""
This module exports a GameControls class that abstracts PyBadge keys
for use in the Tetris game.

>>> gc = GameControls()
>>>
>>> # get keyboard events
>>> event = gc.get_event()
>>>
>>> if event.pressed:
>>>     print('A key was pressed', end='')
>>>
>>>     if event.key_number == gc.keymap.start:
>>>         print('...and that key was the "start" key', end='')
>>>
>>>    print('!)
>>>
>>> elif event.released:
>>>     print('A key was released!')
"""

# disable import errors on my IDE, since my host is running CPython and not CircuitPython
import board  # pylint: disable=import-error
import keypad  # pylint: disable=import-error

class Keymap:
    """
    Abstract the pybadge keys into decipherable names.
    """

    # At some point, this could possibly be abstracted to other boards
    # by using os.uname().machine

    # keys, in matrix order
    keymap = ['B', 'A', 'start', 'select', 'right', 'down', 'up', 'left']

    def __getattr__(self, key):
        if key in self.keymap:
            return self.keymap.index(key)

        raise AttributeError("'{}' has no attribute '{}".format(self.__class__.__name__, key))

class GameControls:
    """
    Provide game control key inputs for the Tetris game.
    """
    keymap = Keymap()

    keys = keypad.ShiftRegisterKeys(
        clock=board.BUTTON_CLOCK, data=board.BUTTON_OUT, latch=board.BUTTON_LATCH, key_count=8,
        value_when_pressed=True
    )

    def get_event(self):
        """
        Get a key event from the keyboard of this class.
        """
        return self.keys.events.get()
