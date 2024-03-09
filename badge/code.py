print("Starting ...")

import math
import os
import time

import board
import terminalio
import displayio
import digitalio
import pwmio
from adafruit_display_text import label
from adafruit_st7735r import ST7735R
from busio import UART

from state import Input, StateMachine
from playing_state import PlayingState
from game_over_state import GameOverState
import sprites
import constants

# Constants
deg10 = math.radians(10)
cos10 = math.cos(deg10)
sin10 = math.sin(deg10)
gravity_acc = 9.81

# Pull down does not work. I.e. False means pressed.
BTN_A = digitalio.DigitalInOut(board.BTN_A)
BTN_A.switch_to_input(pull=digitalio.Pull.UP)

BTN_B = digitalio.DigitalInOut(board.BTN_B)
BTN_B.switch_to_input(pull=digitalio.Pull.UP)

BTN_X = digitalio.DigitalInOut(board.BTN_X)
BTN_X.switch_to_input(pull=digitalio.Pull.UP)

BTN_Y = digitalio.DigitalInOut(board.BTN_Y)
BTN_Y.switch_to_input(pull=digitalio.Pull.UP)

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.CS
tft_dc = board.D1

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.D0)

# https://github.com/adafruit/Adafruit_CircuitPython_ST7735R/blob/main/adafruit_st7735r.py
# Subclasses https://docs.circuitpython.org/en/latest/shared-bindings/displayio/#displayio.Display
# BGR mode means that highest bits are red, meaning that colors can be written as RGB in source.
# Using pwmio.PWMOut and altering duty_cycle to set brightness (cf. factory code) seems to be
# unneccessary boilerblate as the displayio API supports this directly, except that it offers the
# opportunity to light up the display after the CircuitPython logo display.
# Setting upper left pixel shows that the first visible point is indeed 2x1. The usable area is still 128x160.
display = ST7735R(display_bus, width=constants.SCREEN_WIDTH, height=constants.SCREEN_HEIGHT, bgr=True,
    colstart=2, rowstart=1,
    backlight_pin=board.PWM0, brightness=0.5,
    auto_refresh=False)

color_bitmap = displayio.Bitmap(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, 2)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash = displayio.Group()
splash.append(bg_sprite)
display.show(splash)

SYN = bytes([0])
ACK = bytes([0])
SYN_ACK = bytes([1])
PKG_BEGIN = 0xBE
PKG_END = 0xEF
A_BIT = 1
B_BIT = 2

TIMER_START = bytes([1])
TIMER_STOP = bytes([2])
TIMER_RESET = bytes([3])
TIMER_SHOW = bytes([4])
TIMER_HIDE = bytes([5])

uart = UART(baudrate=9600, tx=board.UART_TX2, rx=board.UART_RX2, bits=8, parity=None, stop=1, timeout=0.05)

def send_ready():
    uart.write(ACK)

print("Waiting for controller SYN")
timeout = 10
info_group = None
while uart.read(1) != SYN:
    if timeout > 0:
        timeout -= 1
        if timeout == 0:
            info_group = displayio.Group(scale=1, x=8, y=30)
            info_area = label.Label(terminalio.FONT, text="Press reset on\nMicrobit", color=0xFF0000)
            info_group.append(info_area)
            splash.append(info_group)
            display.refresh()
if info_group is not None:
    splash.remove(info_group)
    display.refresh()

print("Received SYN")
send_ready()
while uart.read(1) != SYN_ACK:
    print("Waiting for controller SYN-ACK")
print("Received SYN-ACK")
send_ready()

def got_pkg_begin():
    b = uart.read(1)
    if b is None:
        return False
    return b[0] == PKG_BEGIN

sprites.load_all()
input = Input()
machine = StateMachine(display, input)
machine.reset_game_state()
machine.add_state(PlayingState())
machine.add_state(GameOverState())
machine.set_state('playing')

while True:
    while not got_pkg_begin():
        pass
    b = uart.read(4)
    if b is None:
        continue

    if len(b) != 4 or b[3] != PKG_END:
        uart.reset_input_buffer()
        send_ready()
        continue
    send_ready()
    btn_state, acc_ctrl_raw_x, acc_ctrl_raw_y, _ = b

    input.btn_ma = btn_state & A_BIT
    input.btn_mb = btn_state & B_BIT
    input.btn_a = not BTN_A.value
    input.btn_b = not BTN_B.value
    input.btn_x = not BTN_X.value
    input.btn_y = not BTN_Y.value

    # Controller sends a value between -1G and 1G for each axis. It's converted to a value between 0 and 0xFE, i.e. 254.
    # Thus zero is 127. Multiply factor of 1G with the gravity constant to get acceleration in m/s^2.
    acc_ctrl_x = (acc_ctrl_raw_x - 127) / 127 * gravity_acc
    # The accelerometer orientation on the Microbit is the opposite of the expected coordinate system.
    # Invert here and keep the  math easier to understand instead of moving parts around.
    acc_ctrl_y = (acc_ctrl_raw_y - 127) / -127 * gravity_acc

    # The Microbit is slightly angled on the board.
    input.acc_x = acc_ctrl_x * sin10 - acc_ctrl_y * cos10
    # Because of the orientation of the Y-axis, the acceleration is inverted.
    input.acc_y = -(acc_ctrl_x * cos10 + acc_ctrl_y * sin10)

    machine.update()

    # The time precision gets too low if we don't have any latency.
    time.sleep(0.05)
