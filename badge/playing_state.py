import displayio

from state import State
from sprites import sprites
import constants

hero_max_x = constants.SCREEN_WIDTH - constants.HERO_WIDTH
hero_max_y = constants.SCREEN_HEIGHT - constants.HERO_HEIGHT
sprite_tilt_acc = 0.7

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
        base_bitmap = displayio.Bitmap(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, 1)
        base_palette = displayio.Palette(1)
        base_tilegrid = displayio.TileGrid(base_bitmap, pixel_shader=base_palette)
        self.hero_sprite = sprites['hero']
        self.hero_group = displayio.Group()
        self.hero_group.append(self.hero_sprite)
        self.root_group = displayio.Group()
        self.root_group.append(base_tilegrid)
        self.root_group.append(self.hero_group)

    def enter(self, machine):
        self.hero_group.x = int(machine.pos_x)
        self.hero_group.y = int(machine.pos_y)
        machine.display.show(self.root_group)

    def update(self, machine):
        self.update_positition(machine)
        self.update_sprite(machine)
        machine.display.refresh()


    def update_positition(self, machine):
        input = machine.input
        time_diff = machine.time_diff
        machine.vel_x += input.acc_x * time_diff * physics_scale
        machine.vel_y += input.acc_y * time_diff * physics_scale

        dx = machine.vel_x * time_diff * px_per_m
        dy = machine.vel_y * time_diff * px_per_m

        nx_tmp = machine.pos_x + dx
        ny_tmp = machine.pos_y + dy

        if nx_tmp < 0 or nx_tmp > 128 - constants.HERO_WIDTH:
            machine.vel_x *= -bounce_factor
        if ny_tmp < 0 or ny_tmp > 160 - constants.HERO_HEIGHT:
            machine.vel_y *= -bounce_factor

        machine.pos_x = max(min(nx_tmp, hero_max_x), 0)
        machine.pos_y = max(min(ny_tmp, hero_max_y), 0)

        self.hero_group.x = int(machine.pos_x)
        self.hero_group.y = int(machine.pos_y)


    def update_sprite(self, machine):
        input = machine.input
        if input.acc_x < -sprite_tilt_acc:
            x = 0
        elif input.acc_x > sprite_tilt_acc:
            x = 2
        else:
            x = 1
        if input.acc_y < -sprite_tilt_acc:
            y = 0
        elif input.acc_y > sprite_tilt_acc:
            y = 2
        else:
            y = 1
        i = 3 * y + x
        self.hero_sprite[0] = i
