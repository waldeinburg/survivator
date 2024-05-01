import displayio

from state import State
from sprites import sprites
from util import LEFT, RIGHT, UP, DOWN, get_time_diff
import microbit
import constants

TIME_PER_SPRITE = 100

class GameOverState(State):
    @property
    def name(self):
        return 'game-over'

    def __init__(self):
        self.hero_explode_sprite = sprites['hero-explode']
        self.hero_explode_group = displayio.Group()
        self.hero_explode_group.append(self.hero_explode_sprite)
        self.did_cleanup = False


    def enter(self, machine):
        if machine.score > machine.highscore:
            machine.highscore = machine.score
            microbit.put_highscore(machine.score)

        # Reset variables that may affect active enemies in rare cases.
        machine.shields[UP].active = False
        machine.shields[DOWN].active = False
        machine.shields[LEFT].active = False
        machine.shields[RIGHT].active = False
        machine.weapon_active = False

        self.hero_explode_group.x = int(machine.pos_x - (constants.HERO_EXPLODE_WIDTH - constants.HERO_WIDTH) / 2)
        self.hero_explode_group.y = int(machine.pos_y - (constants.HERO_EXPLODE_HEIGHT - constants.HERO_HEIGHT) / 2)
        machine.play_area_group.append(self.hero_explode_group)
        machine.hero_explode_sprite_idx = 0
        self.hero_explode_sprite[0] = machine.hero_explode_sprite_idx
        machine.hero_explode_last_update = machine.cur_time


    def exit(self, machine):
        if not self.did_cleanup:
            self.cleanup(machine)
        self.did_cleanup = False


    def cleanup(self, machine):
        if machine.hero_explode_sprite_idx is not None:
            machine.play_area_group.remove(self.hero_explode_group)
        for e in machine.enemies:
            e.destroy(machine)
        self.did_cleanup = True


    def update(self, machine):
        self.update_sprite(machine)
        if machine.input.btn_mb:
            self.cleanup(machine) # Cleanup before game state reset.
            machine.reset_game_state()
            machine.set_state('playing')
            return
        self.update_enemies(machine)
        machine.display.refresh()


    def update_sprite(self, machine):
        if machine.hero_explode_sprite_idx == 9:
            machine.play_area_group.remove(self.hero_explode_group)
            machine.hero_explode_sprite_idx = None
        if machine.hero_explode_sprite_idx is None:
            return
        self.hero_explode_sprite[0] = machine.hero_explode_sprite_idx
        if machine.hero_explode_sprite_idx < 9 and get_time_diff(machine.hero_explode_last_update, machine.cur_time) >= TIME_PER_SPRITE:
            machine.hero_explode_last_update = machine.cur_time
            machine.hero_explode_sprite_idx += 1


    def update_enemies(self, machine):
        for enemy in machine.enemies:
            enemy.update(machine)
