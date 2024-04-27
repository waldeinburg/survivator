import math

from enemy import Enemy
from sprites import sprites
import constants
from util import LEFT, RIGHT, UP, DOWN, get_hero_center, get_direction_to_hero

radius = constants.ROCKET_SIZE / 2
hit_distance = (constants.HERO_SIZE + constants.ROCKET_SIZE) / 2
destroy_distance = constants.WEAPON_RADIUS + radius

class RocketEnemy(Enemy):

    def can_add(side, start_x, start_y, machine):
        return not machine.rocket


    def __init__(self, side, start_x, start_y, machine):
        super().__init__(side, start_x, start_y, machine)
        machine.rocket = True

        self.hit = False
        self.destroyed = False
        self.acceleration = 2500
        self.init_speed = 80
        self.max_speed = self.init_speed

        self.sprite = sprites['rocket']
        self.sprite[0] = 0

        if side == LEFT or side == RIGHT:
            self.cy = start_y
            if side == LEFT:
                self.cx = -radius
            else:
                self.cx = constants.PLAY_WIDTH + radius
        else:
            self.cx = start_x
            if side == UP:
                self.cy = -radius
            else:
                self.cy = constants.PLAY_HEIGHT + radius
        self.group.x = round(self.cx - radius)
        self.group.y = round(self.cy - radius)

        self.group.append(self.sprite)

        self.vel_x, self.vel_y, *_ = get_direction_to_hero(self.cx, self.cy, self.init_speed, machine)


    def destroy(self, machine):
        self.group.remove(self.sprite)
        machine.rocket = False


    def distance_to_hero(self, machine):
        hx, hy = get_hero_center(machine)
        return math.sqrt((hx - self.cx)**2 + (hy - self.cy)**2)


    def update_enemy(self, machine):
        if machine.weapon_active and self.distance_to_hero(machine) < destroy_distance:
            self.destroyed = True
        if self.destroyed:
            return
        time_diff_sec = machine.time_diff / 1000
        if not self.hit:
            acc_x, acc_y, *_ = get_direction_to_hero(self.cx, self.cy, self.acceleration, machine)
            self.vel_x += acc_x * time_diff_sec
            self.vel_y += acc_y * time_diff_sec
        self.vel_x = min(self.vel_x, self.max_speed)
        self.vel_y = min(self.vel_y, self.max_speed)
        self.cx += self.vel_x * time_diff_sec
        self.cy += self.vel_y * time_diff_sec
        self.group.x = round(self.cx - radius)
        self.group.y = round(self.cy - radius)


    def has_hit(self, machine):
        if self.destroyed:
            return False
        if self.hit:
            return True
        hx, hy = get_hero_center(machine)
        if self.distance_to_hero(machine) < hit_distance:
            self.hit = True
        return self.hit
