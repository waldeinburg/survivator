import displayio

from state import State
from sprites import sprites
import constants

TIME_PER_SPRITE = 0.1

class GameOverState(State):
    @property
    def name(self):
        return 'game-over'

    def __init__(self):
        self.hero_explode_sprite = sprites['hero-explode']
        self.hero_explode_group = displayio.Group()
        self.hero_explode_group.append(self.hero_explode_sprite)


    def enter(self, machine):
        self.hero_explode_group.x = int(machine.pos_x - (constants.HERO_EXPLODE_WIDTH - constants.HERO_WIDTH) / 2)
        self.hero_explode_group.y = int(machine.pos_y - (constants.HERO_EXPLODE_HEIGHT - constants.HERO_HEIGHT) / 2)
        machine.play_area_group.append(self.hero_explode_group)
        machine.hero_explode_sprite_idx = 0
        self.hero_explode_sprite[0] = machine.hero_explode_sprite_idx
        machine.hero_explode_last_update = machine.cur_time


    def exit(self, machine):
        if machine.hero_explode_sprite_idx is not None:
            machine.play_area_group.remove(self.hero_explode_group)


    def update(self, machine):
        self.update_sprite(machine)
        if machine.input.btn_mb:
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
        if machine.hero_explode_sprite_idx < 9 and machine.cur_time - machine.hero_explode_last_update >= TIME_PER_SPRITE:
            machine.hero_explode_last_update = machine.cur_time
            machine.hero_explode_sprite_idx += 1


    def update_enemies(self, machine):
        for enemy in machine.enemies:
            enemy.update(machine)
