# Design inspired by / stolen from https://learn.adafruit.com/circuitpython-101-state-machines
import time


class Input:
    def __init__(self):
        self.btn_a = False
        self.btn_b = False
        self.btn_x = False
        self.btn_y = False
        self.btn_ma = False
        self.btn_mb = False
        self.acc_x = 0.0
        self.acc_y = 0.0


class State:
    @property
    def name(self):
        return ''

    def enter(self, machine):
        pass

    def exit(self, machine):
        pass

    def update(self, machine):
        pass


class StateMachine:
    def __init__(self, display, input):
        self.state = None
        self.states = {}
        self.display = display
        self.input = input


    def reset_game_state(self):
        # Timing
        self.cur_time = time.monotonic()
        self.prev_time = time.monotonic()
        self.time_diff = 0.0

        # Game
        self.pos_x = 64.0
        self.pos_y = 80.0
        self.vel_x = 0.0
        self.vel_y = 0.0

        # Enemies
        self.waiting_for_first_enemy = True
        self.enemies = []
        self.enemy_add_time = time.monotonic()
        self.enemy_time_gap = 5


    def add_state(self, state):
        self.states[state.name] = state


    def set_state(self, name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[name]
        self.state.enter(self)


    def update(self):
        new_time = time.monotonic()
        self.time_diff = new_time - self.cur_time;
        self.cur_time = new_time
        self.state.update(self)
