import displayio
import constants

def load_sprite(name, width, height, tile_width, tile_height, default_tile, transparency=True):
    bitmap = displayio.OnDiskBitmap('/assets/' + name + '.bmp')
    if transparency:
        bitmap.pixel_shader.make_transparent(0)
    sprite = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader,
        width=1, height=1, tile_width=constants.HERO_WIDTH, tile_height=constants.HERO_HEIGHT,
        default_tile=4)
    return sprite


sprites = {}

def load_all():
    sprites['hero'] = load_sprite(
        'hero',
        width=1, height=1,
        tile_width=constants.HERO_WIDTH, tile_height=constants.HERO_HEIGHT,
        default_tile=4)
