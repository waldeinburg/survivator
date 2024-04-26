import math

from enemy import Enemy
from sprites import sprites
import constants
from util import LEFT, RIGHT, UP, DOWN, get_hero_center, get_direction_to_hero

radius = constants.ROCKET_SIZE / 2


class RocketEnemy(Enemy):

    def can_add(side, start_x, start_y, machine):
        return not machine.rocket


    def __init__(self, side, start_x, start_y, machine):
        super().__init__(side, start_x, start_y, machine)
        machine.rocket = True

        self.hit = False
        self.destroyed = False
        self.acceleration = 10
        self.init_speed = 50
        self.max_speed = 100

        self.sprite = sprites['rocket']
        self.sprite[0] = 0

        if side == LEFT or side == RIGHT:
            self.y = start_y
            if side == LEFT:
                self.x = -radius
            else:
                self.x = constants.PLAY_WIDTH + radius
        else:
            self.x = start_x
            if side == UP:
                self.y = -radius
            else:
                self.y = constants.PLAY_HEIGHT + radius
        self.group.x = round(self.x - radius)
        self.group.y = round(self.y - radius)

        self.group.append(self.sprite)

        self.vel_x, self.vel_y, *_ = get_direction_to_hero(self.x, self.y, self.init_speed, machine)


    def destroy(self, machine):
        self.group.remove(self.sprite)
        machine.rocket = False


    def update_enemy(self, machine):
        if machine.weapon_active:
            self.destroyed = True
        if self.destroyed:
            return
        time_diff_sec = machine.time_diff / 1000
        acc_x, acc_y, *_ = get_direction_to_hero(self.x, self.y, self.acceleration, machine)
        self.vel_x += acc_x * time_diff_sec
        self.vel_y += acc_y * time_diff_sec
        self.vel_x = min(self.vel_x, self.max_speed)
        self.vel_y = min(self.vel_y, self.max_speed)
        self.x += self.vel_x * time_diff_sec
        self.y += self.vel_y * time_diff_sec
        self.group.x = round(self.x - radius)
        self.group.y = round(self.y - radius)


    def has_hit(self, machine):
        if self.destroyed:
            return False
        if self.hit:
            return True
