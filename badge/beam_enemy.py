import math
from random import randrange

import displayio
from adafruit_display_shapes.line import Line

from enemy import Enemy
import constants
from util import get_random_pos_opposite_hero, get_hero_center

max_x = constants.SCREEN_WIDTH - 1
max_y = constants.SCREEN_HEIGHT - 1

class BeamEnemy(Enemy):

    def __init__(self, machine):
        super().__init__()
        self.speed = 100
        self.color = 0x00FF00
        self.fading = False

        self.start_x, self.start_y = get_random_pos_opposite_hero(machine)
        self.cur_x = self.start_x
        self.cur_y = self.start_y
        aim_x, aim_y = get_hero_center(machine)
        # Calculate velocity x and y based on angle of speed vector.
        # Because we aim for the center, the diff will never be 0.
        dx = aim_x - self.start_x
        dy = aim_y - self.start_y
        a = math.atan(dy / dx)
        dir_x = 1 if dx > 0 else -1
        dir_y = 1 if dx > 0 else -1
        self.vel_x = self.speed * math.cos(a) * dir_x
        self.vel_y = self.speed * math.sin(a) * dir_y


    def update(self, machine):
        if self.fading:
            # Dissolve the line by deleting random parts.
            for i in range(10):
                if len(self.group) > 0:
                    i = randrange(0, len(self.group))
                    del self.group[i]
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
