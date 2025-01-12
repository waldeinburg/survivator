import displayio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

import terminalio
import random

from state import State
from sprites import sprites
from beam_enemy import BeamEnemy
from firewall_enemy import FirewallEnemy
from rocket_enemy import RocketEnemy
import constants
from util import LEFT, RIGHT, UP, DOWN, sides, get_random_side_pos, now, get_time_diff, format_time

first_enemy_appear = 1_000
score_almost_high = 5_000
shield_active_time = 2_000
shield_recharge_time = 500
shield_fading_time = 1_500
weapon_recharge_time = 500
weapon_active_time = 100
hero_max_x = constants.PLAY_WIDTH - constants.HERO_WIDTH
hero_max_y = constants.PLAY_HEIGHT - constants.HERO_HEIGHT
sprite_tilt_acc = 0.7

# Based on feeling
bounce_factor = 0.31
# 100 ms and a start gap of 5 seconds would give 50 enemies before the gap reaches 0 and the screen is flooded.
# This means an absolute max playing time of (2*5 + (5/0.1 - 1)*-0.1) / 2* 5/0.1 = 127.5 seconds.
# A value of 10 ms means a max playing time of almost 21 minutes which gives reasonable space for beating a
# highscore by more than just fractions of seconds.
# A value of 500 gives 27.5 seconds before the flood.
enemy_time_gap_shrink = 10

class PlayingState(State):
    @property
    def name(self):
        return 'playing'


    def __init__(self):
        self.hero_sprite = sprites['hero']
        self.hero_group = displayio.Group()
        self.hero_group.append(self.hero_sprite)

        self.shield_sprites = {}
        self.add_shield_sprites(UP, (constants.SHIELD_WIDTH - constants.HERO_WIDTH) // -2, -constants.SHIELD_DEPTH)
        self.add_shield_sprites(RIGHT, constants.HERO_WIDTH, (constants.SHIELD_WIDTH - constants.HERO_HEIGHT) // -2)
        self.add_shield_sprites(DOWN, (constants.SHIELD_WIDTH - constants.HERO_WIDTH) // -2, constants.HERO_HEIGHT)
        self.add_shield_sprites(LEFT, -constants.SHIELD_DEPTH, (constants.SHIELD_WIDTH - constants.HERO_HEIGHT) // -2)

        self.weapon_sprite = sprites['weapon']
        self.weapon_sprite.x = -(constants.WEAPON_WIDTH - constants.HERO_WIDTH) // 2
        self.weapon_sprite.y = -(constants.WEAPON_HEIGHT - constants.HERO_HEIGHT) // 2
        self.hero_group.append(self.weapon_sprite)


    def add_shield_sprites(self, orientation, x, y):
        s = sprites['shield'][orientation]
        s.hidden = True
        s.x = x
        s.y = y
        self.shield_sprites[orientation] = s
        self.hero_group.append(s)


    def enter(self, machine):
        self.hero_group.x = int(machine.pos_x)
        self.hero_group.y = int(machine.pos_y)

        self.weapon_sprite.hidden = True

        for s in sides:
            self.reset_shield(s)

        machine.play_root_group = displayio.Group()

        machine.play_info_group = displayio.Group()

        info_bg = Rect(x=0, y=0, width=constants.SCREEN_WIDTH, height=constants.INFO_HEIGHT, fill=0x303050)
        machine.play_info_group.append(info_bg)

        high_text = label.Label(terminalio.FONT, color=0xA0A0A0, anchor_point=(0.0, 1.0), anchored_position=(1, constants.INFO_HEIGHT))
        high_text.text = format_time(machine.highscore)
        machine.play_info_group.append(high_text)
        self.score_text = label.Label(terminalio.FONT, color=0xFF0000, anchor_point=(1.0, 1.0), anchored_position=(constants.SCREEN_WIDTH - 1, constants.INFO_HEIGHT))
        self.score_text.text = format_time(0)
        machine.play_info_group.append(self.score_text)


        machine.play_area_group = displayio.Group(y=constants.INFO_HEIGHT)
        machine.enemy_warning_group = displayio.Group()
        machine.play_area_group.append(machine.enemy_warning_group)
        machine.play_area_group.append(self.hero_group)

        # Info group should be on top because of sprites starting there position outside of play area.
        machine.play_root_group.append(machine.play_area_group)
        machine.play_root_group.append(machine.play_info_group)

        machine.display.show(machine.play_root_group)


    def reset_shield(self, orientation):
        s = self.shield_sprites[orientation]
        s.hidden = True
        s[0] = 0


    def exit(self, machine):
        machine.play_area_group.remove(self.hero_group)


    def update(self, machine):
        self.update_score(machine)

        self.update_shield(machine, machine.input.btn_a, UP)
        self.update_shield(machine, machine.input.btn_y, RIGHT)
        self.update_shield(machine, machine.input.btn_b, DOWN)
        self.update_shield(machine, machine.input.btn_x, LEFT)

        if not machine.is_hit:
            i = 0
            while i < len(machine.enemies):
                if machine.enemies[i].is_active(machine):
                    i += 1
                    continue
                # Remove and continue to next by not incrementing i
                machine.enemies_evaded += 1
                enemy = machine.enemies.pop(i)
                machine.play_area_group.remove(enemy.group)
                enemy.destroy(machine)

            for enemy in machine.enemies:
                if enemy.has_hit(machine):
                    machine.is_hit = True
                    break

        if not machine.is_hit:
            self.update_positition(machine)
            self.update_weapon(machine)
            self.update_sprite(machine)
            self.update_enemies(machine)
            self.maybe_add_enemy(machine)

        machine.display.refresh()
        if machine.is_hit:
            machine.set_state('game-over')


    def update_score(self, machine):
        machine.score = get_time_diff(machine.start_time, machine.cur_time)
        self.score_text.text = format_time(machine.score)
        # Change color from red if gaining a highscore.
        if machine.score > machine.highscore:
            self.score_text.color = 0x00FF00
        elif machine.score >= machine.highscore - score_almost_high:
            self.score_text.color = 0xFFFF00


    def update_shield(self, machine, button, orientation):
        shield = machine.shields[orientation]
        if shield.active:
            if not button or get_time_diff(shield.active_time, machine.cur_time) > shield_active_time:
                shield.active = False
                shield.inactive_time = machine.cur_time
                self.shield_sprites[orientation].hidden = True
            elif button and get_time_diff(shield.active_time, machine.cur_time) > shield_fading_time:
                self.shield_sprites[orientation][0] = 1
        elif button and get_time_diff(shield.inactive_time, machine.cur_time) > shield_recharge_time:
            shield.active = True
            shield.active_time = machine.cur_time
            self.shield_sprites[orientation][0] = 0
            self.shield_sprites[orientation].hidden = False


    def update_weapon(self, machine):
        if not machine.weapon_active and \
                machine.input.btn_ma and \
                get_time_diff(machine.weapon_active_time, machine.cur_time) > weapon_recharge_time:
            machine.weapon_active = True
            machine.weapon_active_time = machine.cur_time
            self.weapon_sprite.hidden = False
        if machine.weapon_active and get_time_diff(machine.weapon_active_time, machine.cur_time) > weapon_active_time:
            machine.weapon_active = False
            self.weapon_sprite.hidden = True


    def update_positition(self, machine):
        input = machine.input
        time_diff_sec = machine.time_diff / 1000
        machine.vel_x += input.acc_x * time_diff_sec * constants.PHYSICS_SCALE
        machine.vel_y += input.acc_y * time_diff_sec * constants.PHYSICS_SCALE

        dx = machine.vel_x * time_diff_sec * constants.PX_PER_M
        dy = machine.vel_y * time_diff_sec * constants.PX_PER_M

        nx_tmp = machine.pos_x + dx
        ny_tmp = machine.pos_y + dy

        if nx_tmp < 0 or nx_tmp > constants.PLAY_WIDTH - constants.HERO_WIDTH:
            machine.vel_x *= -bounce_factor
        if ny_tmp < 0 or ny_tmp > constants.PLAY_HEIGHT - constants.HERO_HEIGHT:
            machine.vel_y *= -bounce_factor

        machine.pos_x = max(min(nx_tmp, hero_max_x), 0)
        machine.pos_y = max(min(ny_tmp, hero_max_y), 0)

        self.hero_group.x = round(machine.pos_x)
        self.hero_group.y = round(machine.pos_y)


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
        if get_time_diff(machine.enemy_add_time, machine.cur_time) < \
               (machine.enemy_time_gap if not machine.waiting_for_first_enemy else first_enemy_appear):
            return
        machine.enemy_time_gap = max(machine.enemy_time_gap - enemy_time_gap_shrink, 1)
        machine.waiting_for_first_enemy = False
        machine.enemy_add_time = now()
        enemy = self.get_random_enemy(machine)
        machine.enemies.append(enemy)
        machine.play_area_group.append(enemy.group)
        machine.enemies_launched += 1


    def get_random_enemy(self, machine):
        side, x, y = get_random_side_pos()
        enemy_type = random.choice((BeamEnemy, FirewallEnemy, RocketEnemy))
        # If this type cannot be added with those parameters, default to BeamEnemy.
        if not enemy_type.can_add(side, x, y, machine):
            return BeamEnemy(side, x, y, machine)
        return enemy_type(side, x, y, machine)


    def update_enemies(self, machine):
        for enemy in machine.enemies:
            enemy.update(machine)
