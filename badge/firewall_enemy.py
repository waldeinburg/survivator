import displayio
from random import randrange
import math

from enemy import Enemy
from sprites import sprites
import constants
from util import LEFT, RIGHT, UP, DOWN, get_time_diff

MIN_X = -constants.FIREWALL_DEPTH
MIN_Y = -constants.FIREWALL_DEPTH
MAX_X = constants.PLAY_WIDTH + constants.FIREWALL_DEPTH
MAX_Y = constants.PLAY_HEIGHT + constants.FIREWALL_DEPTH

# Avoid syncronized animation of multiple walls by using an uneven number.
TIME_PER_SPRITE = 113

class FirewallEnemy(Enemy):

    def can_add(side, start_x, start_y, machine):
        return not machine.firewalls[side]


    def __init__(self, side, start_x, start_y, machine):
        super().__init__(side, start_x, start_y, machine)
        self.init_speed = 100

        if side == LEFT or side == RIGHT:
            self.cur_y = 0
            self.vel_y = 0
            self.size = constants.FIREWALL_VER_SIZE
            self.tiles = constants.FIREWALL_VER_TILES
            if side == LEFT:
                self.cur_x = MIN_X
                self.vel_x = self.init_speed
            else:
                self.cur_x = MAX_X
                self.vel_x = -self.init_speed
        elif side == UP or side == DOWN:
            self.cur_x = 0
            self.vel_x = 0
            self.size = constants.FIREWALL_HOR_SIZE
            self.tiles = constants.FIREWALL_HOR_TILES
            if side == UP:
                self.cur_y = MIN_Y
                self.vel_y = self.init_speed
            else:
                self.cur_y = MAX_Y
                self.vel_y = -self.init_speed

        self.side = side
        machine.firewalls[side] = True
        self.sprite = sprites['firewall'][side]
        self.last_update_time = machine.cur_time
        self.randomize_tiles()
        self.group.x = self.cur_x
        self.group.y = self.cur_y
        self.group.append(self.sprite)


    def update_enemy(self, machine):
        if get_time_diff(self.last_update_time, machine.cur_time) >= TIME_PER_SPRITE:
            self.last_update_time = machine.cur_time
            self.randomize_tiles()

        time_diff_sec = machine.time_diff / 1000
        dx = self.vel_x * time_diff_sec
        dy = self.vel_y * time_diff_sec
        self.cur_x = self.cur_x + dx
        self.cur_y = self.cur_y + dy
        self.group.x = round(self.cur_x)
        self.group.y = round(self.cur_y)

        if self.cur_x < MIN_X or self.cur_x > MAX_X or self.cur_y < MIN_Y or self.cur_y > MAX_Y:
            self.active = False


    def randomize_tiles(self):
        for i in range(0, self.size):
            self.sprite[i] = randrange(0, self.tiles)
            self.flip_y = randrange(0, 2) == 1


    def destroy(self, machine):
        self.group.remove(self.sprite)
        machine.firewalls[self.side] = False

