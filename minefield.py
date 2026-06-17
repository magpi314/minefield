import random
import pygame
import os
import math

pygame.init()

# from lib.animations import Animation
from lib.game import Game
from lib.animations import *
from lib.tiles import build_tiles
from lib.util import git_blit


# TODO: Add a volume constant?


# Used only for displaying FPS
font = pygame.font.SysFont("Arial", 18, bold=True)


def fps_counter(surface, clock):
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps, 1, pygame.Color("RED"))
    surface.blit(fps_t, (0, 0))


screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h
win_wide = screen_width // 1.5
win_high = win_wide * 9 // 21
window = pygame.display.set_mode((win_wide, win_high), pygame.NOFRAME)


char_size = window.get_width() * 10 // 417
char_width = char_size * 3 // 5
char_height = char_size * 10 // 9

tile = build_tiles(char_height)
# print(tile)


def main():
    window_info = window.get_size()
    window_width, window_height = window_info[0], window_info[1]
    char_width = window.get_width() * 30 // 2085

    pygame.mixer.music.load("music/ambience.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(1.0)

    display_menu = True

    window.fill(BLACK)
    pygame.draw.rect(window, WHITE, (0, 0, window_width, window_height), width=2)

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

    window.blit(
        git_blit("M I N E F I E L D", color=WHITE, size=char_size * 2),
        (window_width // 2 - char_width * 17, char_height * 1),
    )
    window.blit(
        git_blit("an unfair mini-game", color=GREY, size=char_size),
        (window_width // 2 - char_width * 19 / 2, char_height * 3),
    )

    window_background = window.copy()

    center_page = window_height // 2

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
            "Press any key to continue...",
        ]

        longest_line = max(len(instructions[_]) for _ in range(len(instructions)))

        left_margin = (window_width // 2) - char_width * longest_line / 2

        window.blit(window_background, (0, 0))

        for index, instruction in enumerate(instructions):
            window.blit(
                git_blit(instruction, color=WHITE),
                (
                    left_margin,
                    center_page - char_height * (len(instructions) // 2 - index - 1),
                ),
                size=char_height,
            )
        window.blit(
            git_blit("xXx", color=RED, bg_color=BLACK),
            (
                left_margin + char_width * 16,
                center_page - char_height * (len(instructions) // 2 - 4),
            ),
            size=char_height,
        )
        window.blit(
            git_blit("=@=", color=[YELLOW, GREEN, YELLOW], bg_color=BLACK),
            (
                left_margin + char_width * 18,
                center_page - char_height * (len(instructions) // 2 - 5),
            ),
            size=char_height,
        )
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

    def display_menu(menu, selection=0):
        while True:
            longest_line = (
                max(len(menu[_]) for _ in range(len(menu))) + 2
            )  # with buffer!

            selection %= len(menu)

            window.blit(window_background, (0, 0))

            for i, item in enumerate(menu):
                x, y = (
                    window_width // 2 - char_width * len(item) / 2,
                    center_page + i * char_height - len(menu) * char_height / 2,
                )
                if i == selection:
                    window.blit(
                        git_blit("[", color=WHITE, size=char_height),
                        (window_width // 2 - char_width * longest_line / 2, y),
                    )
                    window.blit(
                        git_blit("]", color=WHITE, size=char_height),
                        (
                            window_width // 2
                            + char_width * longest_line / 2
                            - char_width,
                            y,
                        ),
                    )
                window.blit(git_blit(item, color=WHITE, size=char_height), (x, y))

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
                    menu = ["CONTINUE", "INSTRUCTIONS", "QUIT"]
                    start = False
                    while not start:
                        selection = display_menu(menu)

                        if menu[selection] == "CONTINUE":
                            return
                        elif menu[selection] == "INSTRUCTIONS":
                            give_instructions()
                        elif menu[selection] == "QUIT":
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

    menu = ["START GAME", "INSTRUCTIONS", "QUIT"]

    start = False

    while not start:
        selection = display_menu(menu)

        if menu[selection] == "START GAME":
            start = True
        elif menu[selection] == "INSTRUCTIONS":
            give_instructions()
        elif menu[selection] == "QUIT":
            pygame.quit()
            exit()

    def draw_line(line, y):
        for index, cell in enumerate(line):
            if cell in tile:
                window.blit(tile[cell], (field_left + index * (3 * char_width), y))

    game = Game(char_width, char_height)
    game.init()

    base_line = window_height // 2
    field_left = (window_width // 2) - (game.field_width * 3 * char_width) // 2
    field_right = (window_width // 2) + (game.field_width * 3 * char_width) // 2
    right_panel = field_right + char_width * 1
    left_panel = field_left - char_width * 12
    river_halfheight = (window_height // 2) // char_height

    playing = True
    while playing:
        if True:
            window.fill(BLACK)
            pygame.draw.rect(
                window, WHITE, (0, 0, window_width, window_height), width=2
            )
            fps_counter(window, game.clock)
            # print(clock.tick(60))
            # clock.tick(120)

            window.blit(
                git_blit("GAME OVER", color=game.go_color.value, size=char_height),
                (left_panel, base_line + char_height * 1),
            )

            offset = game.offset.value

            for y in range(1 - river_halfheight, river_halfheight - 1):
                if y < 1 - river_halfheight / 2 or y > river_halfheight / 2:
                    draw_line(
                        [BOG] * game.field_width, base_line + char_height * y + offset
                    )
                else:
                    draw_line(
                        [FOG] * game.field_width, base_line + char_height * y + offset
                    )

            draw_line(game.last_line, base_line + char_height + offset)
            draw_line(game.next_line, base_line - char_height + offset)
            draw_line(game.current_line, base_line + offset)

            window.blit(
                tile[game.player_anim.value],
                (
                    field_left + char_width + game.current_position * (3 * char_width),
                    base_line + offset + game.player_shake.value,
                ),
            )
            if game.player_anim.value != PLAYER and game.hit_points <= 0:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        div = random.randint(3, 5)
                        window.blit(
                            tile[game.player_anim.value],
                            (
                                field_left
                                + char_width
                                + game.current_position * (3 * char_width)
                                + game.player_shake.value * dx,
                                base_line + offset + game.player_shake.value * dy,
                            ),
                        )
            else:  # + dx * char_width // div , + dy * char_height // div
                window.blit(
                    tile[game.player_anim.value],
                    (
                        field_left
                        + char_width
                        + game.current_position * (3 * char_width),
                        base_line + offset + game.player_shake.value,
                    ),
                )

            if game.floater_timer.value and game.last_hit != 0:
                sign = "" if game.last_hit < 0 else "+"
                window.blit(
                    git_blit(
                        f"{sign}{game.last_hit}",
                        color=game.floater_color.value,
                        size=char_height,
                    ),
                    (
                        field_left
                        + char_width
                        + game.current_position * (3 * char_width),
                        base_line + offset + game.hp_floater.value,
                    ),
                )

            # health_color = (200 - max(game.hit_points, 0), max(game.hit_points, 0) // 2, max(game.hit_points, 0) * 2, 255)
            for color in [BLUE, WHITE]:
                shake_mult = (100 - max(game.hit_points, 0)) / 100
                window.blit(
                    git_blit("M I N E F I E L D", color=color, size=char_size * 2),
                    (
                        window_width // 2
                        - char_width * 17
                        + game.title_shake.value * shake_mult,
                        char_height * 1
                        + game.title_shake.value * shake_mult * random.randint(-1, 1),
                    ),
                )
            window.blit(
                git_blit("an unfair mini-game", color=GREY, size=char_height),
                (window_width // 2 - char_width * 19 / 2, char_height * 3),
            )

            window.blit(
                git_blit(
                    f"HP: {game.hit_points}",
                    color=game.hp_color.value,
                    size=char_height,
                ),
                (left_panel, base_line - char_height * 1),
            )
            window.blit(
                git_blit(f"LEVEL: {game.level}", color=WHITE, size=char_height),
                (left_panel, base_line - char_height * 0),
            )
            if game.hit_points > 0:
                window.blit(
                    git_blit(
                        "[←] [↑] [→] TO MOVE", color=WHITE, size=char_size * 4 // 5
                    ),
                    (right_panel, base_line - char_height * 1),
                )
            else:
                window.blit(
                    git_blit("VESSEL DESTROYED", color=WHITE, size=char_height),
                    (right_panel, base_line - char_height * 1),
                )
            window.blit(
                git_blit("[SPACE] TO RESTART", color=WHITE, size=char_size * 4 // 5),
                (right_panel, base_line - char_height * 0),
            )
            window.blit(
                git_blit("[ESC] FOR MAIN MENU", color=WHITE, size=char_size * 4 // 5),
                (right_panel, base_line + char_height * 1),
            )
            window.blit(
                git_blit(game.msg, color=game.msg_color.value, size=char_height),
                (right_panel, base_line + char_height * 2),
            )

            pygame.display.flip()

        process_events()
        game.tick()


if __name__ == "__main__":
    main()
