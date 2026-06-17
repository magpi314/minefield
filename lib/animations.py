import random

# from .game import Game
from .consts import *


class Animation(object):
    def __init__(
        self, game, name: str, frames: list, delay: int, loops: int, static_frame
    ):
        self.game = game
        self.name = name
        self.frames = frames
        self.fps = FPS / delay
        self.static_frame = static_frame
        self.time_passed = -1.0
        self.loops = loops
        self.loop_count = 0
        self.value = static_frame
        self.playing = False

    def start(self):
        self.time_passed = 0.0

    def blink(self):
        # print(f"In {self.name}.blink()")
        if (
            self.time_passed < 0
            or self.time_passed > len(self.frames) * (1 / self.fps) * self.loops
        ):
            self.value = self.static_frame
            return self.static_frame
        else:
            self.time_passed += self.game.clock.get_time() / 1000.0
            ticker = int(self.time_passed * self.fps % len(self.frames))
            self.value = self.frames[ticker]
            # self.value = self.game.blink(self.frames, self.delay)
            return self.value


class Timer(Animation):
    def __init__(self, game, time):
        super().__init__(game, "Timer", [True], time, 1, False)


class Shakes(Animation):
    def __init__(self, game, name: str, max_value: float, length: int):
        colors = [random.randint(-max_value, max_value) for _ in range(length)]
        super().__init__(game, name, colors, 1, 1, 0)


class Move(Animation):
    def __init__(self, game, name: str, values: tuple, delay):
        self.values = values
        min_val = values[0]
        max_val = values[1]
        step = values[2]
        frames = [x for x in range(min_val, max_val, step)]
        super().__init__(game, name, frames, delay, 1, max_val)


class TextColor(Animation):
    def __init__(
        self, game, name: str, colors: list, delay: int, loops: int, static_frame
    ):
        super().__init__(game, name, colors, delay, loops, static_frame)


class PlayerAnimation(Animation):
    def __init__(
        self, game, name: str, colors: list, delay: int, loops: int, static_frame
    ):
        super().__init__(game, name, colors, delay, loops, static_frame)
