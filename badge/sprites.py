import displayio
import adafruit_imageload

import constants

def _load_sprite(name, width, height, tile_width, tile_height, default_tile, transparency=True):
    bitmap, palette = adafruit_imageload.load('/assets/' + name + '.bmp')
    if transparency:
        palette.make_transparent(0)
    sprite = displayio.TileGrid(bitmap, pixel_shader=palette,
        width=width, height=height, tile_width=tile_width, tile_height=tile_height,
        default_tile=default_tile)
    return sprite


def _load_shield_sprite(flip_y, transpose_xy):
    s = _load_sprite(
        'shield',
        width=1, height=1,
        tile_width=constants.SHIELD_WIDTH, tile_height=constants.SHIELD_DEPTH,
        default_tile=0)
    s.flip_y = flip_y
    s.transpose_xy = transpose_xy
    return s


def _load_firewall_sprite(tile_size, width, height, flip_x, flip_y, transpose_xy):
    s = _load_sprite(
        'firewall',
        width=width, height=height,
        tile_width=constants.FIREWALL_DEPTH, tile_height=tile_size,
        default_tile=0)
    s.flip_x = flip_x
    s.flip_y = flip_y
    s.transpose_xy = transpose_xy
    return s


sprites = {}

def load_all():
    sprites['hero'] = _load_sprite(
        'hero',
        width=1, height=1,
        tile_width=constants.HERO_WIDTH, tile_height=constants.HERO_HEIGHT,
        default_tile=4)
    sprites['hero-explode'] = _load_sprite(
        'hero-explode',
        width=1, height=1,
        tile_width=constants.HERO_EXPLODE_WIDTH, tile_height=constants.HERO_EXPLODE_HEIGHT,
        default_tile=0)
    sprites['shield'] = {
        'top': _load_shield_sprite(False, False),
        'right': _load_shield_sprite(True, True),
        'bottom': _load_shield_sprite(True, False),
        'left': _load_shield_sprite(False, True)
    }
    sprites['firewall'] = {
        'top': _load_firewall_sprite(constants.FIREWALL_HOR_TILE_SIZE, 1, constants.FIREWALL_HOR_SIZE, True, False, True),
        'right': _load_firewall_sprite(constants.FIREWALL_VER_TILE_SIZE, 1, constants.FIREWALL_VER_SIZE, False, False, False),
        'bottom': _load_firewall_sprite(constants.FIREWALL_HOR_TILE_SIZE, 1, constants.FIREWALL_HOR_SIZE, False, True, True),
        'left': _load_firewall_sprite(constants.FIREWALL_VER_TILE_SIZE, 1, constants.FIREWALL_VER_SIZE, True, True, False),
    }
