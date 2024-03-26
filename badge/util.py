import math
from random import randrange, choice
import time

import constants

HERO_MIDDLE_X = constants.HERO_WIDTH / 2
HERO_MIDDLE_Y = constants.HERO_HEIGHT / 2

LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'
sides = (LEFT, RIGHT, UP, DOWN)


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
            _get_random_pos(machine.pos_x, constants.PLAY_WIDTH),
            _get_opposite_pos(machine.pos_y, constants.PLAY_HEIGHT)
        )
    else:
        return (
            _get_opposite_pos(machine.pos_x, constants.PLAY_WIDTH),
            _get_random_pos(machine.pos_y, constants.PLAY_HEIGHT)
        )


def _get_random_x():
    return randrange(0, constants.PLAY_WIDTH)


def _get_random_y():
    return randrange(0, constants.PLAY_HEIGHT)


def get_random_side_pos():
    side = choice(sides)
    if side is LEFT:
        return side, 0, _get_random_y()
    if side is RIGHT:
        return side, constants.PLAY_WIDTH - 1, _get_random_y()
    if side is UP:
        return side, _get_random_x(), 0
    if side is DOWN:
        return side, _get_random_x(), constants.PLAY_HEIGHT - 1


def get_hero_center(machine):
    return (
        machine.pos_x + HERO_MIDDLE_X,
        machine.pos_y + HERO_MIDDLE_Y
    )


# Time functions. Always use these so that we can shift from time.monotonic to supervisor.ticks_ms to be able to run precisely after 1 hour.
def now():
    return time.monotonic()


def time_diff(a, b):
    return b - a


def format_time(time):
    '''
    Format time only with necessary parts.
    '''
    # The system has some bad floating point handling (int(4.123 * 1000) == 4122).
    # We could get the digits from str(time) but it would be slower and we will loose the precision while
    # converting from float to int while saving anyway.
    # TODO: read/write highscore as string instead of milliseconds int.
    res = ''
    sec = int(time)
    h = sec // 3600
    hr = sec % 3600
    m = hr // 60
    s = hr % 60
    if h > 0:
        res = str(h) + ':'
        if m < 10:
            res += '0'
    if m > 0 or h > 0:
        res += str(m) + ':'
        if s < 10:
            res += '0'

    ms = int((time - sec) * 1000)
    ms100 = int(ms / 100)
    ms10 = int((ms - ms100 * 100) / 10)
    ms1 = ms - ms10 * 10 - ms100 * 100

    res += str(s) + '.' + str(ms100) + str(ms10) + str(ms1)

    return res
