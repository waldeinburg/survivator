import math
from random import randrange

import constants

HERO_MIDDLE_X = constants.HERO_WIDTH / 2
HERO_MIDDLE_Y = constants.HERO_HEIGHT / 2


def _get_random_pos(hero_pos, max_pos):
        if hero_pos < max_pos / 2:
            pos_min = math.ceil(max_pos / 2)
            pos_max = max_pos
        else:
            pos_min = 0
            pos_max = math.floor(max_pos / 2)
        return randrange(pos_min, pos_max)


def _get_opposite_pos(hero_pos, max_pos):
        if hero_pos < max_pos / 2:
            return max_pos
        else:
            return 0


def get_random_pos_opposite_hero(machine):
    x_or_y = randrange(0, 2)
    if x_or_y == 0:
        return (
            _get_random_pos(machine.pos_x, constants.SCREEN_WIDTH),
            _get_opposite_pos(machine.pos_y, constants.SCREEN_HEIGHT)
        )
    else:
        return (
            _get_opposite_pos(machine.pos_x, constants.SCREEN_WIDTH),
            _get_random_pos(machine.pos_y, constants.SCREEN_HEIGHT)
        )


def get_hero_center(machine):
    return (
        machine.pos_x + HERO_MIDDLE_X,
        machine.pos_y + HERO_MIDDLE_Y
    )
