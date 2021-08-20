Tetris with Circuit Python and the Adafruit PyBadge!
====================================================

The logic for this game was inspired by `this article <https://levelup.gitconnected.com/writing-tetris-in-python-2a16bddb5318>`_. I also picked up some
tips on how to do things using `todbot's staroids <https://github.com/todbot/circuitpython_staroids>`_ project on Github.

This has been manually tested on CircuitPython v7.0.0-alpha.6.

.. raw:: html

  <img src="./docs/pybadge_in_action.jpg" />

Installation
::::::::::::

- Download and install CircuitPython_ >= v7.0.0-alpha.6.

.. _CircuitPython: https://circuitpython.org/board/pybadge/

- Install the required CircuitPython libraries listed in requirements.txt.
- Copy all python files and the tetris.mp3 file to your CIRCUITPY drive

  .. code:: bash

    cp *.py tetris.mp3 [your CircuitPython directory]

  or just manually move all the \*.py files and the tetris.mp3 file over to your
  board using your favorite file explorer and you're off and running!

- If the sound ever gets too annoying, just delete the mp3 file in your
  CircuitPython directory and the sound will stop.

  .. code:: bash

    rm [your CircuitPython directory]/tetris.mp3

Game Controls
:::::::::::::
- The arrow keys control moving the active piece on the board.
- The A button rotates the active piece right and the B button rotates the
  active piece left.
- Press start to pause and select to start another game.

Game Piece Colors
:::::::::::::::::
I have tried to color the pieces with as much contrast as possible, but admit
that I am not color blind and do not have trouble discerning between colors.
You can change the color pieces by changing the RGB tuples in the colors tuple
in util.py.  Adding more colors will add more colored pieces.  PRs with a better
palette of colors are always welcome!

Battery Monitor
:::::::::::::::
I know very little about microcontrollers and am just learning.  As such, I
would not rely on the battery monitor too much, as I don't know if it works or
if it's specific to the battery that I'm using.  I thought that it would be a
neat experiment and isn't based on science as much as a few empirical
observations of my battery draining over time.

Potential Improvements
::::::::::::::::::::::
- splash screen in the beginning
- add tests
- turn neopixels red when battery charge is critically low
- extend to other boards
- support other versions of CircuitPython
