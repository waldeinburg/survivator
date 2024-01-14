import displayio

def load_sprite(name, transparency=True):
    bitmap = displayio.OnDiskBitmap('/assets/' + name + '.bmp')
    if transparency:
        bitmap.pixel_shader.make_transparent(0)
    sprite = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
    return sprite


sprites = {}

def load_all():
    sprites['hero'] = load_sprite('hero')
