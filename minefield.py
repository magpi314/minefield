import random
import pygame
import os
import math

pygame.init()
pygame.mixer.init()

screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h
win_wide = screen_width // 1.5
win_high = win_wide * 9 // 21
window = pygame.display.set_mode((win_wide, win_high), pygame.NOFRAME)

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 200, 0, 255)
BLUE = (50, 50, 200, 255)
YELLOW = (255, 255, 0, 255)
GREY = (200, 200, 250, 255)

EMPTY = 0
MINES = 1
FOG = 2
PLAYER = 3
POWERUP = 4
BOG = 5
EXPLOSION = 6
DEBRIS = 7
NONE = 8
DEAD_PLAYER = 9

LEFT = 0
RIGHT = 1

char_size = window.get_width() * 10 // 417
char_width = char_size * 3 // 5
char_height = char_size * 10 // 9

tile = {}

def git_blit(text, font_name = 'monospace', color = WHITE, bg_color = None, size = char_size, rotate = 0):
    width = int(3 * size / 5)
    font = pygame.font.SysFont(font_name, int(3 * size / 4))
    render_surface = pygame.Surface((width * len(text), size), pygame.SRCALPHA).convert_alpha()
    for index, chr in enumerate(text):
        c = color if type(color) == tuple else color[index % len(color)]
        text_surface = font.render(chr, True, c, bg_color)
        if rotate != 0:
            text_surface = pygame.transform.rotate(text_surface, rotate)
        render_surface.blit(text_surface, (width * index, 0))
    return render_surface

tile[EMPTY] = git_blit("...", color = (205, 205, 255))
tile[MINES] = git_blit("xXx", color = RED, bg_color = BLACK)
tile[FOG] = git_blit("...", color = (100, 100, 150))
tile[PLAYER] = git_blit("@", bg_color = BLACK)
tile[POWERUP] = git_blit("=@=", color = [YELLOW, GREEN, YELLOW], bg_color = BLACK)
tile[BOG] = git_blit("...", color = (50, 50, 50))
tile[EXPLOSION] = git_blit("*", color = (200, 50, 50), bg_color = BLACK)
tile[DEBRIS] = git_blit("#", color = (255, 50, 0))
tile[NONE] = pygame.Surface((0,0))
tile[DEAD_PLAYER] = git_blit("@", color = (255, 255, 255), rotate = 180)

def clip_sound(original_sound, start_sec, end_sec):
    """Clips a pygame.mixer.Sound object and returns a new Sound object."""
    raw_data = original_sound.get_raw()
    
    # Each sample is 2 bytes (16-bit) multiplied by the number of channels (stereo=2, mono=1)
    # This formula calculates byte indices based on Pygame's default sound settings.
    sample_rate = pygame.mixer.get_init()[0]
    channels = pygame.mixer.get_init()[2]
    bytes_per_sample = 2 * channels 
    
    start_byte = int(start_sec * sample_rate * bytes_per_sample)
    end_byte = int(end_sec * sample_rate * bytes_per_sample)
    
    # Ensure byte indices align to a whole sample boundary
    start_byte -= start_byte % bytes_per_sample
    end_byte -= end_byte % bytes_per_sample
    
    # Slice the raw bytestring
    clipped_data = raw_data[start_byte:end_byte]
    
    return pygame.mixer.Sound(buffer=clipped_data)

powerup_sound = pygame.mixer.Sound('sound/powerup.mp3')
explosion_sound = pygame.mixer.Sound('sound/explosion.mp3')
big_explosion_sound = pygame.mixer.Sound('sound/big_explosion.mp3')
diving_sound = clip_sound(pygame.mixer.Sound('sound/dive.mp3'), 0, 0.5)
dying_sound = pygame.mixer.Sound('sound/explosion_bubbles.mp3')

class Game(object):
    def __init__(self, field_width = 9, current_position = 5, current_line = None, last_line = None, next_line = None, hit_points = 100, level = 0, msg = ""):
        self.field_width = field_width
        self.current_position = current_position
        self.current_line = [EMPTY] * self.field_width if current_line is None else current_line
        self.last_line = [EMPTY] * self.field_width if last_line is None else last_line
        self.next_line = [random.randint(EMPTY, MINES) for _ in range(field_width)] if next_line is None else next_line
        self.hit_points = hit_points
        self.level = level
        self.msg = ""
        self.frame = 0
        self.last_advance = 0
        self.animations = []
        self.player_anim = None
        self.last_hit = 0

        pygame.mixer.music.load('music/game_theme.wav')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(1.0)

    def init(self):
        self.player_anim = PlayerAnimation(self, [DEAD_PLAYER, EXPLOSION, DEBRIS], 20, 1, PLAYER)
        self.floater_timer = Timer(self, 150)
        self.hp_color = TextColor(self, [RED, WHITE], 50, 2, WHITE)
        self.go_color = TextColor(self, [WHITE, RED], 50, math.inf, BLACK)
        self.msg_color = TextColor(self, [RED, WHITE, YELLOW], 50 // 3, 2, WHITE)
        self.vd_color = TextColor(self, [(55 + b * 10, 55 + b * 10, 255) for b in range(20, 0, -1)], 20, 1, WHITE)
        self.floater_color = TextColor(self,[RED, WHITE], 20, math.inf, WHITE)
        self.title_shake = Shakes(self, char_width // 2, 80)
        self.player_shake = Shakes(self, char_height // 2, 20)
        self.offset = Move(self, (- char_height, 0, char_height // 8), 1)
        self.hp_floater = Move(self, (- char_height, - 2 * char_height, - 1), 5)
        self.animations = [
            self.player_anim,                                                                   # PlayerAnimation
            self.floater_timer,                                                                 # Timer
            self.hp_color, self.go_color, self.msg_color, self.vd_color, self.floater_color,    # TextColor
            self.title_shake, self.player_shake,                                                # Shakes
            self.offset, self.hp_floater                                                        # Move
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
                pygame.mixer.Channel(0).play(diving_sound)
                pygame.mixer.Channel(0).queue(dying_sound)
                pygame.mixer.Channel(1).play(big_explosion_sound)
                pygame.mixer.Channel(1).play(explosion_sound)
            else:
                pygame.mixer.Channel(0).play(explosion_sound)
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
            pygame.mixer.Sound.play(powerup_sound)

    def level_advance(self):
        if self.hit_points > 0:
            self.last_advance = self.frame
            self.last_line = self.current_line
            self.current_line = self.next_line
            self.next_line = [random.randint(EMPTY, MINES) for _ in range(self.field_width)]
            self.level += 1
            self.offset.start()
            self.check_space()

    def move(self, direction):
        if self.hit_points > 0:
            if direction == LEFT and self.current_position > 0 and self.hit_points > 0:
                self.current_position -= 1
            elif direction == RIGHT and self.current_position < self.field_width - 1 and self.hit_points > 0:
                self.current_position += 1
            self.check_space()

    def plop(self, item, position = None):
        position = random.randint(0, self.field_width - 1) if position is None else position
        if self.hit_points > 0:
            self.next_line[position] = item

    def blink(self, colors: list, blink_delay: int):
        ticker = (self.frame % (blink_delay * len(colors))) // blink_delay
        color = colors[ticker]
        return color

    def tick(self):
        self.frame += 1
        for animation in self.animations:
            animation.blink()

class Animation(object):
    def __init__(self, game: Game, frames: list, delay: int, loops: int, static_frame):
        self.game = game
        self.frames = frames
        self.delay = delay
        self.static_frame = static_frame
        self.key_frame = -1
        self.loops = loops
        self.loop_count = 0
        self.value = static_frame
        self.playing = False
    
    def start(self):
        self.key_frame = self.game.frame

    def blink(self):
        if  self.key_frame < 0 or self.game.frame - self.key_frame > self.delay * len(self.frames) * self.loops:
            self.value = self.static_frame
            return self.static_frame
        else:
            self.value = self.game.blink(self.frames, self.delay)
            return self.value

class Timer(Animation):
    def __init__(self, game, time):
        super().__init__(game, [True], time, 1, False)

class Shakes(Animation):
    def __init__(self, game: Game, max_value: float, length: int):
        colors = [random.randint(- max_value, max_value) for _ in range(length)]
        super().__init__(game, colors, 1, 1, 0)

class Move(Animation):
    def __init__(self, game: Game, values: tuple, delay):
        self.values = values
        min_val = values[0]
        max_val = values[1]
        step = values[2]
        frames = [x for x in range(min_val, max_val, step)]
        super().__init__(game, frames, delay, 1, max_val)
    def blink(self):
        if  self.key_frame < 0 or self.game.frame - self.key_frame > self.delay * len(self.frames) * self.loops:
            self.value = self.static_frame
            return self.static_frame
        else:
            ticker = ((self.game.frame - self.key_frame) // self.delay) - 1
            dynamic_frame = self.frames[ticker]
            self.value = dynamic_frame
            return self.value

class TextColor(Animation):
    def __init__(self, game: Game, colors: list, delay: int, loops:int, static_frame):
        super().__init__(game, colors, delay, loops, static_frame)

class PlayerAnimation(Animation):
    def __init__(self, game: Game, colors: list, delay: int, loops:int, static_frame):
        super().__init__(game, colors, delay, loops, static_frame)

def main():

    window_info = window.get_size()
    window_width, window_height = window_info[0], window_info[1]
    char_width = window.get_width() * 30 // 2085

    pygame.mixer.music.load('music/ambience.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    display_menu = True

    window.fill(BLACK)
    pygame.draw.rect(window, WHITE, (0, 0, window_width, window_height), width = 2)


    big_empty = pygame.transform.scale2x(tile[EMPTY])
    big_mines = pygame.transform.scale2x(tile[MINES])
    big_powerup = pygame.transform.scale2x(tile[POWERUP])
    big_empty.set_alpha(30)
    big_mines.set_alpha(30)
    big_powerup.set_alpha(30)

    for x in range(-100, window_width + 100, big_empty.get_width()):
        for y in range(-100, window_height + 100, big_empty.get_height()):
            aSurface = big_empty.copy() if random.random() <= 0.5 else big_mines.copy()
            aSurface = big_powerup.copy() if random.random() <= 0.01 else aSurface
            window.blit(aSurface, (x, y))

    window.blit(git_blit("M I N E F I E L D", color = WHITE, size = char_size * 2), (window_width // 2 - char_width * 17, char_height * 1))
    window.blit(git_blit("an unfair mini-game", color = GREY), (window_width // 2 - char_width * 19 / 2, char_height * 3))

    window_background = window.copy()
 
    center_page = (window_height // 2)

    def give_instructions():

        instructions = [
            "Use the arrow keys to move left, right, or forward.",
            "You cannot move backward,",
            "and you cannot see mines greater than one level away.",
            "Avoid the mines xXx or you will lose HP.",
            "Collect power-ups =@= to restore HP.",
            "The game ends when your HP reaches zero.",
            "Try to get as far as you can!",
            " ",
            "Press any key to continue..."
        ]

        longest_line = max(len(instructions[_]) for _ in range(len(instructions)))   

        left_margin = (window_width // 2) - char_width * longest_line / 2

        window.blit(window_background, (0, 0))

        for index, instruction in enumerate(instructions):
            window.blit(git_blit(instruction, color = WHITE), (left_margin, center_page - char_height * (len(instructions) // 2 - index - 1)))
        window.blit(git_blit("xXx", color = RED, bg_color = BLACK), (left_margin + char_width * 16, center_page - char_height * (len(instructions) // 2 - 4)))
        window.blit(git_blit("=@=", color = [YELLOW, GREEN, YELLOW], bg_color = BLACK), (left_margin + char_width * 18, center_page - char_height * (len(instructions) // 2 - 5)))
        pygame.display.flip()

        anykey = False
        while not anykey:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    anykey = True

    def display_menu(menu, selection = 0):

        while True:

            longest_line = max(len(menu[_]) for _ in range(len(menu))) + 2 # with buffer!

            selection %= len(menu)

            window.blit(window_background, (0, 0))

            for i, item in enumerate(menu):
                x, y = window_width // 2 - char_width * len(item) / 2, center_page + i * char_height - len(menu) * char_height / 2
                if i == selection:
                    window.blit(git_blit('[', color = WHITE), (window_width // 2 - char_width * longest_line / 2, y))
                    window.blit(git_blit(']', color = WHITE), (window_width // 2 + char_width * longest_line / 2 - char_width, y))                
                window.blit(git_blit(item, color = WHITE), (x, y))

            pygame.display.flip()

            anykey = False
            while not anykey:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            menu = False
                            pygame.quit()
                            exit()
                        elif event.key == pygame.K_UP:
                            selection -= 1
                        elif event.key == pygame.K_DOWN:
                            selection += 1
                        elif event.key == pygame.K_RETURN:
                            return selection                  
                        anykey = True

    def process_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    
                    menu = [
                        'CONTINUE',
                        'INSTRUCTIONS',
                        'QUIT'
                    ]
                    start = False
                    while not start:
                        selection = display_menu(menu)

                        if menu[selection] == 'CONTINUE':
                            return
                        elif menu[selection] == 'INSTRUCTIONS':
                            give_instructions()
                        elif menu[selection] == 'QUIT':
                            pygame.quit()
                            exit()

                elif event.key == pygame.K_LEFT:
                    game.move(LEFT)
                elif event.key == pygame.K_RIGHT:
                    game.move(RIGHT)
                elif event.key == pygame.K_UP:
                    game.level_advance()
                    if game.level >= 5 and random.random() < 0.1:
                        game.plop(POWERUP)
                elif event.key == pygame.K_SPACE or event.key == pygame.K_r:
                    game.init()

    menu = [
        'START GAME',
        'INSTRUCTIONS',
        'QUIT'
    ]

    start = False

    while not start:
        selection = display_menu(menu)

        if menu[selection] == 'START GAME':
            start = True
        elif menu[selection] == 'INSTRUCTIONS':
            give_instructions()
        elif menu[selection] == 'QUIT':
            pygame.quit()
            exit()

    def draw_line(line, y):
        for index, cell in enumerate(line):
            if cell in tile:
                window.blit(tile[cell], (field_left + index * (3 * char_width), y))

    game = Game()
    game.init()

    base_line = (window_height // 2)
    field_left = (window_width // 2) - (game.field_width * 3 * char_width) // 2
    field_right = (window_width // 2) + (game.field_width * 3 * char_width) // 2
    right_panel = field_right + char_width * 1
    left_panel = field_left - char_width * 12
    river_halfheight = (window_height // 2) // char_height

    playing = True
    while playing:

        if True:

            window.fill(BLACK)
            pygame.draw.rect(window, WHITE, (0, 0, window_width, window_height), width = 2)

            window.blit(git_blit("GAME OVER", color = game.go_color.value), (left_panel, base_line + char_height * 1))

            offset = game.offset.value

            for y in range(1 - river_halfheight, river_halfheight - 1):
                if y < 1 - river_halfheight / 2 or y > river_halfheight / 2:
                    draw_line([BOG] * game.field_width, base_line + char_height * y + offset)                
                else:
                    draw_line([FOG] * game.field_width, base_line + char_height * y + offset)

            draw_line(game.last_line, base_line + char_height + offset)
            draw_line(game.next_line, base_line - char_height + offset)
            draw_line(game.current_line, base_line + offset)

            window.blit(tile[game.player_anim.value], (field_left + char_width + game.current_position * (3 * char_width), base_line + offset + game.player_shake.value))
            if game.player_anim.value != PLAYER and game.hit_points <= 0:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        div = random.randint(3, 5)
                        window.blit(tile[game.player_anim.value], (field_left + char_width + game.current_position * (3 * char_width) + game.player_shake.value * dx, base_line + offset + game.player_shake.value * dy))
            else: # + dx * char_width // div , + dy * char_height // div
                window.blit(tile[game.player_anim.value], (field_left + char_width + game.current_position * (3 * char_width), base_line + offset + game.player_shake.value))


            if game.floater_timer.value and game.last_hit != 0:
                sign = "" if game.last_hit < 0 else "+"
                window.blit(git_blit(f"{sign}{game.last_hit}", color = game.floater_color.value), (field_left + char_width + game.current_position * (3 * char_width), base_line + offset + game.hp_floater.value))

            # health_color = (200 - max(game.hit_points, 0), max(game.hit_points, 0) // 2, max(game.hit_points, 0) * 2, 255)
            for color in [BLUE, WHITE]:
                shake_mult = (100 - max(game.hit_points, 0)) / 100
                window.blit(git_blit("M I N E F I E L D", color = color, size = char_size * 2), (window_width // 2 - char_width * 17 + game.title_shake.value * shake_mult, char_height * 1 + game.title_shake.value * shake_mult * random.randint(-1, 1)))
            window.blit(git_blit("an unfair mini-game", color = GREY), (window_width // 2 - char_width * 19 / 2, char_height * 3))

            window.blit(git_blit(f"HP: {game.hit_points}", color = game.hp_color.value), (left_panel, base_line - char_height * 1))
            window.blit(git_blit(f"LEVEL: {game.level}", color = WHITE), (left_panel, base_line - char_height * 0))
            if game.hit_points > 0:
                window.blit(git_blit("[←] [↑] [→] TO MOVE", color = WHITE, size = char_size * 4 // 5), (right_panel, base_line - char_height * 1))
            else:
                window.blit(git_blit("VESSEL DESTROYED", color = WHITE), (right_panel, base_line - char_height * 1))
            window.blit(git_blit("[SPACE] TO RESTART", color = WHITE, size = char_size * 4 // 5), (right_panel, base_line - char_height * 0))
            window.blit(git_blit("[ESC] FOR MAIN MENU", color = WHITE, size = char_size * 4 // 5), (right_panel, base_line + char_height * 1))
            window.blit(git_blit(game.msg, color = game.msg_color.value), (right_panel, base_line + char_height * 2))
            
            pygame.display.flip()

        process_events()
        game.tick()

if __name__ == "__main__":
    main()
