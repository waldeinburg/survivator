import displayio
from adafruit_display_shapes.rect import Rect

import constants

wait_time = 0.3
warning_blink_on_time = 0.05
warning_blink_off_time = 0.01
warning_size = 1
warning_color = 0xFFFF00


class Enemy:

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
            w_height = constants.SCREEN_HEIGHT
            w_y = 0
            if side == 'LEFT':
                w_x = 0
            else:
                w_x = constants.SCREEN_WIDTH - warning_size
        else:
            w_width = constants.SCREEN_WIDTH
            w_height = warning_size
            w_x = 0
            if side == 'UP':
                w_y = 0
            else:
                w_y = constants.SCREEN_HEIGHT - warning_size
        self.warning.x = w_x
        self.warning.y = w_y
        self.warning.append(Rect(0, 0, w_width, w_height, fill=warning_color))
        machine.enemy_warning_group.append(self.warning)


    def update(self, machine):
        if self.launched:
            self.update_enemy(machine)
        elif machine.cur_time - self.init_time >= wait_time:
            self.launched = True
            machine.enemy_warning_group.remove(self.warning)
        elif not self.warning.hidden and machine.cur_time - self.warning_blink_change_time >= warning_blink_on_time:
            self.warning.hidden = True
            self.warning_blink_change_time = machine.cur_time
        elif self.warning.hidden and machine.cur_time - self.warning_blink_change_time >= warning_blink_off_time:
            self.warning.hidden = False
            self.warning_blink_change_time = machine.cur_time


    def update_enemy(self, machine):
        pass


    def is_active(self, machine):
        return self.active


    def has_hit(self, machine):
        return False
