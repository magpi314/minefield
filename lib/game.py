import random
import pygame
import math

from .consts import *
from .animations import *
from . import audio


class Game(object):
    def __init__(
        self,
        char_width,
        char_height,
        field_width=9,
        current_position=5,
        current_line=None,
        last_line=None,
        next_line=None,
        hit_points=100,
        level=0,
        msg="",
    ):
        self.char_width = char_width
        self.char_height = char_height
        self.field_width = field_width
        self.current_position = current_position
        self.current_line = (
            [EMPTY] * self.field_width if current_line is None else current_line
        )
        self.last_line = [EMPTY] * self.field_width if last_line is None else last_line
        self.next_line = (
            [random.randint(EMPTY, MINES) for _ in range(field_width)]
            if next_line is None
            else next_line
        )
        self.hit_points = hit_points
        self.level = level
        self.msg = ""
        self.frame = 0
        self.last_advance = 0
        self.animations = []
        self.player_anim = None
        self.last_hit = 0
        self.clock = pygame.time.Clock()

        pygame.mixer.music.load("music/game_theme.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(1.0)

    def init(self):
        self.player_anim = PlayerAnimation(
            self, "Player", [DEAD_PLAYER, EXPLOSION, DEBRIS], 20, 1, PLAYER
        )
        self.floater_timer = Timer(self, 150)
        self.hp_color = TextColor(self, "hp_color", [RED, WHITE], 50, 2, WHITE)
        self.go_color = TextColor(self, "go_color", [WHITE, RED], 50, math.inf, BLACK)
        self.msg_color = TextColor(
            self, "msg_color", [RED, WHITE, YELLOW], 50 // 3, 2, WHITE
        )
        self.vd_color = TextColor(
            self,
            "vd_color",
            [(55 + b * 10, 55 + b * 10, 255) for b in range(20, 0, -1)],
            20,
            1,
            WHITE,
        )
        self.floater_color = TextColor(
            self, "Floater color", [RED, WHITE], 20, math.inf, WHITE
        )
        self.title_shake = Shakes(self, "Title shake", self.char_width // 2, 80)
        self.player_shake = Shakes(self, "Player shake", self.char_height // 2, 20)
        self.offset = Move(
            self, "Offset", (-self.char_height, 0, self.char_height // 8), 1
        )
        self.hp_floater = Move(
            self, "HP Floater", (-self.char_height, -2 * self.char_height, -1), 5
        )
        self.animations = [
            self.player_anim,  # PlayerAnimation
            self.floater_timer,  # Timer
            self.hp_color,
            self.go_color,
            self.msg_color,
            self.vd_color,
            self.floater_color,  # TextColor
            self.title_shake,
            self.player_shake,  # Shakes
            self.offset,
            self.hp_floater,  # Move
        ]

        self.frame = 0
        self.last_advance = 0
        self.current_position = 5
        self.current_line = [EMPTY] * self.field_width
        self.last_line = [EMPTY] * self.field_width
        self.next_line = [random.randint(EMPTY, MINES) for _ in range(self.field_width)]
        self.hit_points = 100
        self.level = 0
        self.msg = ""
        self.last_hit = 0

    def check_space(self):
        if self.current_line[self.current_position] == EMPTY:
            self.msg = ""
            self.last_hit = 0
        elif self.current_line[self.current_position] == MINES:
            damage = random.randint(0, 100) if self.hit_points > 0 else 0
            self.hit_points -= damage
            self.last_hit = -damage
            self.floater_color.frames = [RED, WHITE]
            self.msg = "MINE IMPACT!"
            self.hp_color.start()
            self.player_anim.start()
            self.msg_color.start()
            self.title_shake.start()
            self.player_shake.start()
            self.hp_floater.start()
            self.floater_color.start()
            self.floater_timer.start()
            if self.hit_points <= 0:
                self.hp_color.loops = math.inf
                self.msg_color.loops = math.inf
                self.go_color.start()
                self.vd_color.start()
                self.player_anim.static_frame = NONE
                self.player_anim.delay = 30
                self.player_anim.loops = 2
                self.vd_color.static_frame = BLUE
                pygame.mixer.Channel(0).play(audio.diving_sound)
                pygame.mixer.Channel(0).queue(audio.dying_sound)
                pygame.mixer.Channel(1).play(audio.big_explosion_sound)
                pygame.mixer.Channel(1).play(audio.explosion_sound)
            else:
                pygame.mixer.Channel(0).play(audio.explosion_sound)
        elif self.current_line[self.current_position] == POWERUP:
            bonus = random.randint(0, 100)
            self.hit_points = min(self.hit_points + bonus, 100)
            self.last_hit = bonus
            self.floater_color.frames = [GREEN, WHITE]
            self.current_line[self.current_position] = EMPTY
            self.msg = "POWER-UP COLLECT!"
            self.hp_floater.start()
            self.floater_color.start()
            self.floater_timer.start()
            pygame.mixer.Sound.play(audio.powerup_sound)

    def level_advance(self):
        if self.hit_points > 0:
            self.last_advance = self.frame
            self.last_line = self.current_line
            self.current_line = self.next_line
            self.next_line = [
                random.randint(EMPTY, MINES) for _ in range(self.field_width)
            ]
            self.level += 1
            self.offset.start()
            self.check_space()

    def move(self, direction):
        if self.hit_points > 0:
            if direction == LEFT and self.current_position > 0 and self.hit_points > 0:
                self.current_position -= 1
            elif (
                direction == RIGHT
                and self.current_position < self.field_width - 1
                and self.hit_points > 0
            ):
                self.current_position += 1
            self.check_space()

    def plop(self, item, position=None):
        position = (
            random.randint(0, self.field_width - 1) if position is None else position
        )
        if self.hit_points > 0:
            self.next_line[position] = item

    # def blink(self, colors: list, blink_delay: int):
    #     ticker = (self.frame % (blink_delay * len(colors))) // blink_delay
    #     color = colors[ticker]
    #     return color

    # def blink(self, colors: list, fps: float):
    #     ticker = (self.frame % (blink_delay * len(colors))) // blink_delay
    #     color = colors[ticker]
    #     return color

    def tick(self):
        self.clock.tick(FPS)
        self.frame += 1
        for animation in self.animations:
            # print(f"Blinking {animation.name}")
            animation.blink()
