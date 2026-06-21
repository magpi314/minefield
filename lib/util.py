import pygame
from .consts import *


def git_blit(text, font_name="monospace", color=WHITE, bg_color=None, size=1, rotate=0):
    width = int(3 * size / 5)
    font = pygame.font.SysFont(font_name, int(3 * size / 4))
    render_surface = pygame.Surface(
        (width * len(text), size), pygame.SRCALPHA
    ).convert_alpha()
    if bg_color:
        render_surface.fill(bg_color)
    for index, chr in enumerate(text):
        c = color if type(color) == tuple else color[index % len(color)]
        text_surface = font.render(chr, True, c, bg_color)
        if rotate != 0:
            text_surface = pygame.transform.rotate(text_surface, rotate)
        render_surface.blit(text_surface, (width * index, 0))
    return render_surface
