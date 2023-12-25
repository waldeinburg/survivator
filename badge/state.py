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

        # Timing
        self.prev_time = time.monotonic()
        self.time_diff = 0.0

        # Game
        self.pos_x = 64.0
        self.pos_y = 80.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.prev_x = int(self.pos_x)
        self.prev_y = int(self.pos_y)

    def add_state(self, state):
        self.states[state.name] = state

    def set_state(self, name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[name]
        self.state.enter(self)

    def update(self):
        cur_time = time.monotonic()
        self.time_diff = cur_time - self.prev_time;
        self.prev_time = cur_time
        self.state.update(self)
