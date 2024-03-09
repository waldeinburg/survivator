import displayio
import adafruit_imageload

import constants

def load_sprite(name, width, height, tile_width, tile_height, default_tile, transparency=True):
    bitmap, palette = adafruit_imageload.load('/assets/' + name + '.bmp')
    if transparency:
        palette.make_transparent(0)
    sprite = displayio.TileGrid(bitmap, pixel_shader=palette,
        width=1, height=1, tile_width=tile_width, tile_height=tile_height,
        default_tile=4)
    return sprite


sprites = {}

def load_all():
    sprites['hero'] = load_sprite(
        'hero',
        width=1, height=1,
        tile_width=constants.HERO_WIDTH, tile_height=constants.HERO_HEIGHT,
        default_tile=4)
    sprites['hero-explode'] = load_sprite(
        'hero-explode',
        width=1, height=1,
        tile_width=constants.HERO_EXPLODE_WIDTH, tile_height=constants.HERO_EXPLODE_HEIGHT,
        default_tile=0)
