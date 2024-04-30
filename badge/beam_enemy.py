import math
from random import randrange

import displayio
from adafruit_display_shapes.line import Line

from enemy import Enemy
import constants
from util import get_hero_center, get_direction_to_hero, get_distance_to_hero

max_x = constants.PLAY_WIDTH - 1
max_y = constants.PLAY_HEIGHT - 1

class BeamEnemy(Enemy):

    def __init__(self, side, start_x, start_y, machine):
        super().__init__(side, start_x, start_y, machine)
        self.speed = 100
        self.color = 0x00FF00
        self.fading = False

        self.cur_x = self.start_x
        self.cur_y = self.start_y

        self.vel_x, self.vel_y = get_direction_to_hero(self.start_x, self.start_y, self.speed, machine)


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

        time_diff_sec = machine.time_diff / 1000
        dx = self.vel_x * time_diff_sec
        dy = self.vel_y * time_diff_sec
        new_cur_x = max(min(self.cur_x + dx, max_x), 0)
        new_cur_y = max(min(self.cur_y + dy, max_y), 0)

        if new_cur_x == max_x or new_cur_x == 0 or new_cur_y == max_y or new_cur_y == 0:
            self.fading = True

        if int(new_cur_x) != int(self.cur_x) or int(new_cur_y) != int(self.cur_y):
            self.group.append(Line(int(self.cur_x), int(self.cur_y), int(new_cur_x), int(new_cur_y), self.color))
        self.cur_x = new_cur_x
        self.cur_y = new_cur_y


    def has_hit(self, machine):
        return get_distance_to_hero(self.start_x, self.start_y, self.cur_x, self.cur_y, machine) <= constants.HERO_RADIUS
