import math

from enemy import Enemy
from sprites import sprites
import constants
from util import LEFT, RIGHT, UP, DOWN, get_hero_center, get_direction_to_hero, get_distance_to_hero

radius = constants.ROCKET_SIZE / 2
hit_distance = constants.HERO_RADIUS + radius
destroy_distance = constants.WEAPON_RADIUS + radius
min_x = -radius
min_y = -radius
max_x = constants.PLAY_WIDTH + radius
max_y = constants.PLAY_HEIGHT + radius

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
        self.last_cx = self.cx
        self.last_cy = self.cy
        self.group.x = round(self.cx - radius)
        self.group.y = round(self.cy - radius)

        self.group.append(self.sprite)

        self.vel_x, self.vel_y = get_direction_to_hero(self.cx, self.cy, self.init_speed, machine)


    def destroy(self, machine):
        self.group.remove(self.sprite)
        machine.rocket = False


    def update_enemy(self, machine):
        self.last_cx = self.cx
        self.last_c = self.cy
        if machine.weapon_active and self.distance_to_hero(machine) < destroy_distance:
            self.destroyed = True
        if self.destroyed:
            return
        time_diff_sec = machine.time_diff / 1000
        if not self.hit:
            acc_x, acc_y = get_direction_to_hero(self.cx, self.cy, self.acceleration, machine)
            self.vel_x += acc_x * time_diff_sec
            self.vel_y += acc_y * time_diff_sec
        elif self.cx < min_x or self.cx > max_x or self.cy < min_y or self.cy > max_y:
            self.active = False
            return
        # FIXME: This only work to one side. And it needs to limit the size of the vector
        # or else the rocket can travel faster at an angle than horisontally or vertically.
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
        # With high speed the rocket might travel through the point were it actually hits.
        # Use distance to line traveled.
        if get_distance_to_hero(self.last_cx, self.last_cy, self.cx, self.cy, machine) < hit_distance:
            self.hit = True
            self.sprite[0] = 1
        return self.hit
