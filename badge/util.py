import math
from random import randrange, choice
import supervisor
import sys

import constants

HERO_MIDDLE_X = constants.HERO_WIDTH / 2
HERO_MIDDLE_Y = constants.HERO_HEIGHT / 2

LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'
sides = (LEFT, RIGHT, UP, DOWN)


class Retry:
    def __init__(self, max_retries=10):
        self.max_retries = max_retries
        self.retries = 0


    def reset(self):
        self.retries = 0


    def inc(self):
        self.retries += 1
        if self.retries > self.max_retries:
            print('Retries exceeded')
            sys.exit(1)


def dbg(*args):
    if constants.DEBUG:
        print(" ".join(map(str, args)))


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


def get_direction_to_hero(x, y, vector_size, machine):
    aim_x, aim_y = get_hero_center(machine)
    dx = aim_x - x
    if dx == 0:
        dx = 0.000001
    dy = aim_y - y
    angle = math.atan(dy / dx)
    direction = 1 if dx > 0 else -1
    vec_x = vector_size * math.cos(angle) * direction
    vec_y = vector_size * math.sin(angle) * direction
    return vec_x, vec_y


def get_distance_to_hero(x1, y1, x2, y2, machine):
    # https://math.stackexchange.com/a/2250212
    # Shortest distance between the path of the enemy and the path of the hero would be more precise,
    # but is far more complex and could hurt performance. Regard it as a feature: You can, theoretically
    # move so fast that you move through enemies. The other way around doesn't work well: The rocket
    # moves back and forth through the hero until it's slow enough to hit if we just use the distance
    # between enemy and hero location.
    hx, hy = get_hero_center(machine)
    # Avoid division by zero if there's no line.
    if x1 == x2 and y1 == y2:
        return math.sqrt((x1-hx)**2 + (y1-hy)**2)
    t = -((x1-hx)*(x2-x1) + (y1-hy)*(y2-y1)) / ((x2-x1)**2 + (y2-y1)**2)
    if 0 <= t <=1:
        return abs((x2-x1)*(y1-hy) - (y2-y1)*(x1-hx)) / math.sqrt((x2-x1)**2 + (y2-y1)**2)
    return min(math.sqrt((x1-hx)**2 + (y1-hy)**2), math.sqrt((x2-hx)**2 + (y2-hy)**2))


# Time functions using supervisor.ticks_ms to avoid floating point errors from time.monotonic.
# Ticks does NOT necessarily start on 0 at startup! Therefore some code is taken from
# https://docs.circuitpython.org/en/latest/shared-bindings/supervisor/index.html#supervisor.ticks_ms

_TICKS_PERIOD = const(1<<29)
_TICKS_MAX = const(_TICKS_PERIOD-1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

def now():
    return supervisor.ticks_ms()


def time_add(ticks, delta):
    "Add a delta to a base number of ticks, performing wraparound at 2**29ms."
    return (ticks + delta) % _TICKS_PERIOD


def get_time_diff(a, b):
    "Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
    return ((((b - a) & _TICKS_MAX) + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD


def get_one_hour_ago():
    return time_add(now(), -3600_000)


def format_time(time_ms):
    '''
    Format time only with necessary parts.
    '''
    res = ''
    h = time_ms // 3600_000
    hr = time_ms % 3600_000
    m = hr // 60_000
    mr = hr % 60_000
    s = mr // 1000
    ms = mr % 1000
    ms100 = ms // 100
    ms10 = (ms % 100) // 10
    ms1 = ms % 10
    if h > 0:
        res = str(h) + ':'
        if m < 10:
            res += '0'
    if m > 0 or h > 0:
        res += str(m) + ':'
        if s < 10:
            res += '0'
    res += str(s) + '.' + str(ms100) + str(ms10) + str(ms1)
    return res
