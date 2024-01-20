import displayio
from adafruit_display_shapes.line import Line

from enemy import Enemy
import constants
from util import get_random_pos_opposite_hero, get_hero_center


class BeamEnemy(Enemy):

    def __init__(self, machine):
        super().__init__()
        self.speed = 10
        self.color = 0x00FF00

        self.start_x, self.start_y = get_random_pos_opposite_hero(machine)
        self.cur_x = self.start_x
        self.cur_y = self.start_y
        aim_x, aim_y = get_hero_center(machine)
        # Calculate velocity x and y based on angle of speed vector.


    def update(self, machine):
        new_cur_x = 40
        new_cur_y = 40
        if int(new_cur_x) != int(self.cur_x) or int(new_cur_y) != int(self.cur_y):
            self.group.append(Line(int(self.cur_x), int(self.cur_y), int(new_cur_x), int(new_cur_y), self.color))
        self.cur_x = new_cur_x
        self.cur_y = new_cur_y
