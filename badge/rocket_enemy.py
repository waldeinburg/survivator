import math

from enemy import Enemy
from sprites import sprites
import constants
from util import LEFT, RIGHT, UP, DOWN, get_hero_center, get_direction_to_hero, get_distance_to_hero, get_time_diff, get_one_hour_ago

radius = constants.ROCKET_SIZE / 2
hit_distance = constants.HERO_RADIUS + radius
destroy_distance = constants.WEAPON_RADIUS + radius
min_x = -radius
min_y = -radius
max_x = constants.PLAY_WIDTH + radius
max_y = constants.PLAY_HEIGHT + radius

destroy_time_per_sprite = 150

class RocketEnemy(Enemy):

    def can_add(side, start_x, start_y, machine):
        return not machine.rocket


    def __init__(self, side, start_x, start_y, machine):
        super().__init__(side, start_x, start_y, machine)
        machine.rocket = True

        self.hit = False
        self.destroyed = False
        self.destroyed_last_update_time = get_one_hour_ago()
        self.destroy_sprite_idx = 2
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


    def get_distance_to_hero(self, machine):
        return get_distance_to_hero(self.last_cx, self.last_cy, self.cx, self.cy, machine)


    def update_enemy(self, machine):
        self.last_cx = self.cx
        self.last_c = self.cy
        if machine.weapon_active and self.get_distance_to_hero(machine) < destroy_distance:
            self.destroyed = True
            self.sprite[0] = self.destroy_sprite_idx
        if self.destroyed:
            if get_time_diff(self.destroyed_last_update_time, machine.cur_time) >= destroy_time_per_sprite:
                self.destroy_sprite_idx += 1
                if self.destroy_sprite_idx == constants.ROCKET_TILES:
                    self.active = False
                else:
                    self.sprite[0] = self.destroy_sprite_idx
                    self.destroyed_last_update_time = machine.cur_time
            return
        time_diff_sec = machine.time_diff / 1000
        if not self.hit:
            acc_x, acc_y = get_direction_to_hero(self.cx, self.cy, self.acceleration, machine)
            self.vel_x += acc_x * time_diff_sec
            self.vel_y += acc_y * time_diff_sec
        elif self.cx < min_x or self.cx > max_x or self.cy < min_y or self.cy > max_y:
            self.active = False
            return
        speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
        if speed > self.max_speed:
            f = self.max_speed / speed
            self.vel_x *= f
            self.vel_y *= f
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
        if self.get_distance_to_hero(machine) < hit_distance:
            self.hit = True
            self.sprite[0] = 1
        return self.hit
