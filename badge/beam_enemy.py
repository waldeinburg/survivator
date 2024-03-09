import math
from random import randrange

import displayio
from adafruit_display_shapes.line import Line

from enemy import Enemy
import constants
from util import get_hero_center

max_x = constants.SCREEN_WIDTH - 1
max_y = constants.SCREEN_HEIGHT - 1
radius = constants.HERO_SIZE / 2

class BeamEnemy(Enemy):

    def __init__(self, side, start_x, start_y, machine):
        super().__init__(side, start_x, start_y, machine)
        self.speed = 100
        self.color = 0x00FF00
        self.fading = False
        self.active = True

        self.cur_x = self.start_x
        self.cur_y = self.start_y
        self.aim_x, self.aim_y = get_hero_center(machine)
        # Calculate velocity x and y based on angle of speed vector.
        # Because we aim for the center, the diff will never be 0.
        dx = self.aim_x - self.start_x
        dy = self.aim_y - self.start_y
        self.angle = math.atan(dy / dx)
        self.dir_x = 1 if dx > 0 else -1
        self.dir_y = 1 if dx > 0 else -1
        self.vel_x = self.speed * math.cos(self.angle) * self.dir_x
        self.vel_y = self.speed * math.sin(self.angle) * self.dir_y


    def update_enemy(self, machine):
        if self.fading:
            # Dissolve the line by deleting random parts.
            for i in range(10):
                if len(self.group) > 0:
                    i = randrange(0, len(self.group))
                    del self.group[i]
            if len(self.group) == 0:
                self.active = False
            return

        dx = self.vel_x * machine.time_diff
        dy = self.vel_y * machine.time_diff
        new_cur_x = max(min(self.cur_x + dx, max_x), 0)
        new_cur_y = max(min(self.cur_y + dy, max_y), 0)

        if new_cur_x == max_x or new_cur_x == 0 or new_cur_y == max_y or new_cur_y == 0:
            self.fading = True

        if int(new_cur_x) != int(self.cur_x) or int(new_cur_y) != int(self.cur_y):
            self.group.append(Line(int(self.cur_x), int(self.cur_y), int(new_cur_x), int(new_cur_y), self.color))
        self.cur_x = new_cur_x
        self.cur_y = new_cur_y


    def has_hit(self, machine):
        lx = self.cur_x
        ly = self.cur_y
        px, py = get_hero_center(machine)
        dx = lx - px
        dy = ly - py
        a = self.angle

        # Has tip hit?
        point_distance = math.sqrt(dx**2 + dy**2)
        if point_distance <= radius:
            return True
        # Has line passed?
        ldx = lx - self.start_x
        ldy = ly - self.start_y
        dir_ldx = 1 if ldx > 0 else -1
        dir_dx = 1 if dx > 0 else -1
        dir_ldy = 1 if ldy > 0 else -1
        dir_dy = 1 if dy > 0 else -1

        if ldx == 0 or ldy == 0 or dir_ldx + dir_dx == 0 or dir_ldy + dir_dy == 0:
            return False
        # Does line hit?
        line_distance = abs(math.cos(a) * dy - math.sin(a) * dx)
        return line_distance <= radius
