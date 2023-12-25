import displayio

from state import State

# Screen width is 28 mm, resolution 128, i.e.:
px_per_m = 4571
# Factor based on feeling. Is this really some crude application of intertia physics?
# TODO: Brush up 20+ year old physics/math and do this properly. It could improve the feeling of the steering.`
physics_scale = 0.01
# Based on feeling
bounce_factor = 0.31

class PlayingState(State):
    @property
    def name(self):
        return 'playing'

    def __init__(self):
        self.color_bitmap = displayio.Bitmap(128, 160, 2)
        color_palette = displayio.Palette(2)
        color_palette[0] = 0x000000
        color_palette[1] = 0x00FF00
        sprite = displayio.TileGrid(self.color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.group = displayio.Group()
        self.group.append(sprite)

    def enter(self, machine):
        machine.display.show(self.group)

    def update(self, machine):
        input = machine.input
        time_diff = machine.time_diff
        machine.vel_x += input.acc_x * time_diff * physics_scale
        machine.vel_y += input.acc_y * time_diff * physics_scale

        dx = machine.vel_x * time_diff * px_per_m
        dy = machine.vel_y * time_diff * px_per_m

        nx_tmp = machine.pos_x + dx
        ny_tmp = machine.pos_y + dy

        if nx_tmp < 0 or nx_tmp > 127:
            machine.vel_x *= -bounce_factor
        if ny_tmp < 0 or ny_tmp > 159:
            machine.vel_y *= -bounce_factor

        machine.pos_x = max(min(nx_tmp, 127), 0)
        machine.pos_y = max(min(ny_tmp, 159), 0)

        self.move_dot(machine)

    def set_pixel(self, x, y, c):
        self.color_bitmap[x, y] = c

    def move_dot(self, machine):
        self.set_pixel(machine.prev_x, machine.prev_y, 0)
        x = int(machine.pos_x)
        y = int(machine.pos_y)
        self.set_pixel(x, y, 1)
        machine.display.refresh()
        machine.prev_x = x
        machine.prev_y = y
