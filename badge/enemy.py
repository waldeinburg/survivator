import displayio
from adafruit_display_shapes.rect import Rect

import constants
from util import get_time_diff

wait_time = 300
warning_blink_on_time = 50
warning_blink_off_time = 10
warning_size = 1
warning_color = 0xFFFF00


class Enemy:

    def can_add(side, start_x, start_y, machine):
        return True


    def __init__(self, side, start_x, start_y, machine):
        self.group = displayio.Group()
        self.start_x = start_x
        self.start_y = start_y
        self.active = True
        self.launched = False
        self.init_time = machine.cur_time
        self.warning_blink_change_time = machine.cur_time
        self.warning = displayio.Group()
        if side == 'LEFT' or side == 'RIGHT':
            w_width = warning_size
            w_height = constants.PLAY_HEIGHT
            w_y = 0
            if side == 'LEFT':
                w_x = 0
            else:
                w_x = constants.PLAY_WIDTH - warning_size
        else:
            w_width = constants.PLAY_WIDTH
            w_height = warning_size
            w_x = 0
            if side == 'UP':
                w_y = 0
            else:
                w_y = constants.PLAY_HEIGHT - warning_size
        self.warning.x = w_x
        self.warning.y = w_y
        self.warning.append(Rect(0, 0, w_width, w_height, fill=warning_color))
        machine.enemy_warning_group.append(self.warning)


    def update(self, machine):
        if self.launched:
            self.update_enemy(machine)
        elif get_time_diff(self.init_time, machine.cur_time) >= wait_time:
            self.launched = True
            machine.enemy_warning_group.remove(self.warning)
        elif not self.warning.hidden and get_time_diff(self.warning_blink_change_time, machine.cur_time) >= warning_blink_on_time:
            self.warning.hidden = True
            self.warning_blink_change_time = machine.cur_time
        elif self.warning.hidden and get_time_diff(self.warning_blink_change_time, machine.cur_time) >= warning_blink_off_time:
            self.warning.hidden = False
            self.warning_blink_change_time = machine.cur_time


    def destroy(self, machine):
        pass


    def update_enemy(self, machine):
        pass


    def has_hit(self, machine):
        return False


    def is_active(self, machine):
        return self.active

