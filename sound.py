"""
Control playing and stopping the tetris theme song.
"""

# disable import errors on my IDE, since my host is running CPython and not CircuitPython
import audioio  # pylint: disable=import-error
import audiomp3  # pylint: disable=import-error
import board  # pylint: disable=import-error
import digitalio  # pylint: disable=import-error

from tetris import game_state

TETRIS_MP3_FILE = '/tetris.mp3'

speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speaker_enable.switch_to_output(value=True)

class NullAudio:
    """
    Dummy class in case the MP3 file doesn't exist.  Since we're only
    calling methods in the AudioOut instance, just return noops for
    all in __getattr__.
    """
    def __getattr__(self, key):
        return lambda: ()

class SoundController:
    """
    Play the theme song (.play) and stop playing the theme song (.stop)
    """
    def __init__(self):
        try:
            self.tetris_mp3 = audiomp3.MP3Decoder(open(TETRIS_MP3_FILE, "rb"))
            self.audio = audioio.AudioOut(board.SPEAKER)
        except OSError as exc:
            if exc.errno == 2:
                self.audio = NullAudio()
            else:
                raise exc

        self.on_game_state_change(game_state.playing)

    def on_game_state_change(self, state):
        """
        Start or stop music, depending on game state
        """
        if state == game_state.gameover:
            self.audio.stop()
        elif state == game_state.paused:
            self.audio.pause()
        elif state == game_state.playing:
            if self.audio.paused:
                self.audio.resume()
            else:
                self.audio.play(self.tetris_mp3, loop=True)

    def __del__(self):
        self.tetris_mp3.deinit()
        self.audio.deinit()
