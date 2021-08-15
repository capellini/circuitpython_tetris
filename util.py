"""
Utility functions, classes, variables, etc
"""

# Define colors to be used for the game pieces.  Leave (0, 0, 0) as the
# first, but adding more colors (or taking away colors) should result in
# game pieces with more (less) colors.
colors = (
    (0, 0, 0),
    (120, 37, 179),
    (53, 62, 255),
    (151, 28, 202),
    (80, 134, 22),
    (180, 34, 22),
    (253, 152, 38),
)

class CallbackProperty:
    """
    Class to emulate a callback property, which is basically an array of callbacks that
    can be added to or removed from.  I'm only implementing the in-place addition and
    subtraction operators, because those are really the only ones that I need (really I
    only need __iadd__).
    """
    def __init__(self, callbacks=None):
        self.callbacks = callbacks if callbacks is not None else tuple()
        self._iter_index = 0

    @staticmethod
    def _is_valid_callback_property(other):
        """
        Determine if the other argument passed into an operator method is valid.  Valid
        other arguments are either a callable, a list of callables, or another
        CallbackProperty instance.
        """
        return (
            isinstance(other, CallbackProperty) or
            callable(other) or
            (isinstance(other, (list, tuple)) and all(callable(x) for x in other))
        )

    def __add__(self, other):
        raise NotImplementedError('Please use only in-place operators for callback properties')

    def __iadd__(self, other):
        if not self._is_valid_callback_property(other):
            raise ValueError('Invalid callback type')

        if isinstance(other, CallbackProperty):
            callback_list = other.callbacks
        elif isinstance(other, (list, tuple)):
            callback_list = other
        else:
            callback_list = (other, )

        self.callbacks = self.callbacks + callback_list

        return self

    def __sub__(self, other):
        raise NotImplementedError('Please use only in-place operators for callback properties')

    def __isub__(self, other):
        if isinstance(other, CallbackProperty):
            callback_list = other.callbacks
        elif isinstance(other, (list, tuple)):
            callback_list = other
        else:
            callback_list = (other, )

        for callback in callback_list:
            self.callbacks = tuple(x for x in self.callbacks if x != callback)

        return self

    def __iter__(self):
        self._iter_index = 0

        return self

    def __next__(self):
        try:
            result = self.callbacks[self._iter_index]
            self._iter_index += 1

            return result
        except IndexError:
            raise StopIteration  # pylint: disable=raise-missing-from
