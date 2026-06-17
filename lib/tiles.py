import pygame

from .consts import *
from .util import git_blit


def build_tiles(size):
    tile = {}

    tile[EMPTY] = git_blit("...", color=(205, 205, 255), size=size)
    tile[MINES] = git_blit("xXx", color=RED, bg_color=BLACK, size=size)
    tile[FOG] = git_blit("...", color=(100, 100, 150), size=size)
    tile[PLAYER] = git_blit("@", bg_color=BLACK, size=size)
    tile[POWERUP] = git_blit(
        "=@=", color=[YELLOW, GREEN, YELLOW], bg_color=BLACK, size=size
    )
    tile[BOG] = git_blit("...", color=(50, 50, 50), size=size)
    tile[EXPLOSION] = git_blit("*", color=(200, 50, 50), bg_color=BLACK, size=size)
    tile[DEBRIS] = git_blit("#", color=(255, 50, 0), size=size)
    tile[NONE] = pygame.Surface((0, 0))
    tile[DEAD_PLAYER] = git_blit("@", color=(255, 255, 255), rotate=180, size=size)
    return tile
