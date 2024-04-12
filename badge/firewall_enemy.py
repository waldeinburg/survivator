import displayio
from random import randrange
import math

from enemy import Enemy
from sprites import sprites
import constants
from util import LEFT, RIGHT, UP, DOWN, get_time_diff

MIN_X = -constants.FIREWALL_DEPTH
MIN_Y = -constants.FIREWALL_DEPTH
MAX_X = constants.PLAY_WIDTH
MAX_Y = constants.PLAY_HEIGHT

# Avoid syncronized animation of multiple walls by using an uneven number.
TIME_PER_SPRITE = 113

class FirewallEnemy(Enemy):

    def can_add(side, start_x, start_y, machine):
        return not machine.firewalls[side]


    def __init__(self, side, start_x, start_y, machine):
        super().__init__(side, start_x, start_y, machine)
        self.init_speed = 100
        self.hit = False

        if side == LEFT or side == RIGHT:
            self.y = 0
            self.vel_y = 0
            self.size = constants.FIREWALL_VER_SIZE
            self.tiles = constants.FIREWALL_VER_TILES
            if side == LEFT:
                self.x = MIN_X
                self.vel_x = self.init_speed
            else:
                self.x = MAX_X
                self.vel_x = -self.init_speed
        elif side == UP or side == DOWN:
            self.x = 0
            self.vel_x = 0
            self.size = constants.FIREWALL_HOR_SIZE
            self.tiles = constants.FIREWALL_HOR_TILES
            if side == UP:
                self.y = MIN_Y
                self.vel_y = self.init_speed
            else:
                self.y = MAX_Y
                self.vel_y = -self.init_speed

        self.side = side
        machine.firewalls[side] = True
        self.sprite = sprites['firewall'][side]
        self.last_update_time = machine.cur_time
        self.randomize_tiles()
        self.group.x = self.x
        self.group.y = self.y
        self.group.append(self.sprite)


    def destroy(self, machine):
        self.group.remove(self.sprite)
        machine.firewalls[self.side] = False


    def update_enemy(self, machine):
        if get_time_diff(self.last_update_time, machine.cur_time) >= TIME_PER_SPRITE:
            self.last_update_time = machine.cur_time
            self.randomize_tiles()

        if self.side == LEFT and machine.shields[LEFT].active and self.x + constants.FIREWALL_DEPTH >= machine.pos_x - constants.SHIELD_DEPTH:
            self.x = machine.pos_x - constants.SHIELD_DEPTH - constants.FIREWALL_DEPTH
        elif self.side == RIGHT and machine.shields[RIGHT].active and self.x <= machine.pos_x + constants.HERO_WIDTH + constants.SHIELD_DEPTH:
            self.x = machine.pos_x + constants.HERO_WIDTH + constants.SHIELD_DEPTH
        elif self.side == UP and machine.shields[UP].active and self.y + constants.FIREWALL_DEPTH >= machine.pos_y - constants.SHIELD_DEPTH:
            self.y = machine.pos_y - constants.SHIELD_DEPTH - constants.FIREWALL_DEPTH
        elif self.side == DOWN and machine.shields[DOWN].active and self.y <= machine.pos_y + constants.HERO_HEIGHT + constants.SHIELD_DEPTH:
            self.y = machine.pos_y + constants.HERO_HEIGHT + constants.SHIELD_DEPTH
        else:
            time_diff_sec = machine.time_diff / 1000
            dx = self.vel_x * time_diff_sec
            dy = self.vel_y * time_diff_sec
            self.x = self.x + dx
            self.y = self.y + dy
        self.group.x = round(self.x)
        self.group.y = round(self.y)

        if self.x < MIN_X or self.x > MAX_X or self.y < MIN_Y or self.y > MAX_Y:
            self.active = False


    def randomize_tiles(self):
        for i in range(0, self.size):
            self.sprite[i] = randrange(0, self.tiles)
            self.flip_y = randrange(0, 2) == 1


    def has_hit(self, machine):
        if self.hit:
            return True
        self.hit = self.side == LEFT and self.x + constants.FIREWALL_DEPTH >= machine.pos_x or \
            self.side == RIGHT and self.x <= machine.pos_x + constants.HERO_WIDTH or \
            self.side == UP and self.y + constants.FIREWALL_DEPTH >= machine.pos_y or \
            self.side == DOWN and self.y <= machine.pos_y + constants.HERO_HEIGHT
        return self.hit
