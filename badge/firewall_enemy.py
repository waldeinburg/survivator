import displayio
from random import randrange

from enemy import Enemy
from sprites import sprites
import constants
from util import LEFT, RIGHT, UP, DOWN

class FirewallEnemy(Enemy):

    def __init__(self, side, start_x, start_y, machine):
        super().__init__(side, start_x, start_y, machine)

        s = sprites['firewall']
        if side == LEFT:
            self.sprite = s['left']
            self.sprite.x = 10
            self.sprite.y = 0
            self.randomize_tiles(constants.FIREWALL_VER_SIZE, constants.FIREWALL_VER_TILES)
        elif side == RIGHT:
            self.sprite = s['right']
            self.sprite.x = 110
            self.sprite.y = 0
            self.randomize_tiles(constants.FIREWALL_VER_SIZE, constants.FIREWALL_VER_TILES)
        elif side == UP:
            self.sprite = s['top']
            self.sprite.x = 0
            self.sprite.y = 10
            self.randomize_tiles(constants.FIREWALL_HOR_SIZE, constants.FIREWALL_HOR_TILES)
        else: # side == DOWN
            self.sprite = s['bottom']
            self.sprite.x = 0
            self.sprite.y = 130
            self.randomize_tiles(constants.FIREWALL_HOR_SIZE, constants.FIREWALL_HOR_TILES)

        machine.play_area_group.append(self.sprite)


    def randomize_tiles(self, size, tiles):
        for i in range(0, size):
            self.sprite[i] = randrange(0, tiles)
