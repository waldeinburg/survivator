import time

import displayio

from state import State
from sprites import sprites
from beam_enemy import BeamEnemy
import constants
from util import get_random_side_pos

first_enemy_appear = 1
hero_max_x = constants.SCREEN_WIDTH - constants.HERO_WIDTH
hero_max_y = constants.SCREEN_HEIGHT - constants.HERO_HEIGHT
sprite_tilt_acc = 0.7

# Factor based on feeling. Is this really some crude application of intertia physics?
# TODO: Brush up 20+ year old physics/math and do this properly. It could improve the feeling of the steering.`
physics_scale = 0.01
# Based on feeling
bounce_factor = 0.31
# 0.1 and a start gap of 5 seconds would give 50 enemies before the gap reaches 0 and the screen is flooded.
# This means an absolute max playing time of (2*5 + (5/0.1 - 1)*-0.1) / 2* 5/0.1 = 127.5 seconds.
# A value of 0.01 means a max playing time of almost 21 minutes which gives reasonable space for beating a
# highscore by more than just fractions of seconds.
# A value of 0.5 gives 27.5 seconds before the flood.
enemy_time_gap_shrink = 0.01

class PlayingState(State):
    @property
    def name(self):
        return 'playing'


    def __init__(self):
        self.hero_sprite = sprites['hero']
        self.hero_group = displayio.Group()
        self.hero_group.append(self.hero_sprite)


    def enter(self, machine):
        self.hero_group.x = int(machine.pos_x)
        self.hero_group.y = int(machine.pos_y)
        machine.play_root_group = displayio.Group()
        machine.enemy_warning_group = displayio.Group()
        machine.play_root_group.append(machine.enemy_warning_group)
        machine.play_root_group.append(self.hero_group)
        machine.display.show(machine.play_root_group)


    def exit(self, machine):
        machine.play_root_group.remove(self.hero_group)


    def update(self, machine):
        if not machine.is_hit:
            i = 0
            while i < len(machine.enemies):
                if machine.enemies[i].is_active(machine):
                    i += 1
                    continue
                # Remove and continue to next by not incrementing i
                enemy = machine.enemies.pop(i)
                machine.play_root_group.remove(enemy.group)

            for enemy in machine.enemies:
                if enemy.has_hit(machine):
                    machine.is_hit = True
                    break

        if not machine.is_hit:
            self.update_positition(machine)
            self.update_sprite(machine)
            self.update_enemies(machine)
            self.maybe_add_enemy(machine)
        machine.display.refresh()
        if machine.is_hit:
            machine.set_state('game-over')


    def update_positition(self, machine):
        input = machine.input
        time_diff = machine.time_diff
        machine.vel_x += input.acc_x * time_diff * physics_scale
        machine.vel_y += input.acc_y * time_diff * physics_scale

        dx = machine.vel_x * time_diff * constants.PX_PER_M
        dy = machine.vel_y * time_diff * constants.PX_PER_M

        nx_tmp = machine.pos_x + dx
        ny_tmp = machine.pos_y + dy

        if nx_tmp < 0 or nx_tmp > 128 - constants.HERO_WIDTH:
            machine.vel_x *= -bounce_factor
        if ny_tmp < 0 or ny_tmp > 160 - constants.HERO_HEIGHT:
            machine.vel_y *= -bounce_factor

        machine.pos_x = max(min(nx_tmp, hero_max_x), 0)
        machine.pos_y = max(min(ny_tmp, hero_max_y), 0)

        self.hero_group.x = int(machine.pos_x)
        self.hero_group.y = int(machine.pos_y)


    def update_sprite(self, machine):
        input = machine.input
        if input.acc_x < -sprite_tilt_acc:
            x = 0
        elif input.acc_x > sprite_tilt_acc:
            x = 2
        else:
            x = 1
        if input.acc_y < -sprite_tilt_acc:
            y = 0
        elif input.acc_y > sprite_tilt_acc:
            y = 2
        else:
            y = 1
        i = 3 * y + x
        self.hero_sprite[0] = i


    def maybe_add_enemy(self, machine):
        if machine.cur_time - machine.enemy_add_time < \
               (machine.enemy_time_gap if not machine.waiting_for_first_enemy else first_enemy_appear):
            return
        machine.enemy_time_gap = max(machine.enemy_time_gap - enemy_time_gap_shrink, 0)
        machine.waiting_for_first_enemy = False
        machine.enemy_add_time = time.monotonic()
        enemy = self.get_random_enemy(machine)
        machine.enemies.append(enemy)
        machine.play_root_group.append(enemy.group)


    def get_random_enemy(self, machine):
        side, x, y = get_random_side_pos()
        return BeamEnemy(side, x, y, machine)


    def update_enemies(self, machine):
        for enemy in machine.enemies:
            enemy.update(machine)
