print("Starting ...")

import math
import time
import os

import board
import terminalio
import displayio
import digitalio
import pwmio
from adafruit_display_text import label
from adafruit_st7735r import ST7735R
from busio import UART

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
display = ST7735R(display_bus, width=128, height=160, bgr=True, colstart=2, rowstart=1, backlight_pin=board.PWM0, brightness=0.5)

color_bitmap = displayio.Bitmap(128, 160, 2)
color_palette = displayio.Palette(2)
color_palette[0] = 0x000000
color_palette[1] = 0x00FF00
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash = displayio.Group()
splash.append(bg_sprite)
display.show(splash)

deg10 = math.radians(10)
cos10 = math.cos(deg10)
sin10 = math.sin(deg10)
# Screen width is 28 mm, resolution 128, i.e.:
px_per_m = 4571
# Decisions based on feeling.
physics_scale = 0.14
bounce_factor = 0.31

prev_acc_x = 0
prev_acc_y = 0
pos_x = 64.0
pos_y = 80.0
vel_x = 0
vel_y = 0
prev_x = int(pos_x)
prev_y = int(pos_y)

def set_pixel(x, y, c):
    color_bitmap[y * 128 + x] = c

# TODO: double-buffer
def move_dot(x, y):
    global prev_x, prev_y
    set_pixel(prev_x, prev_y, 0)
    set_pixel(x, y, 1)
    prev_x = x
    prev_y = y


SYN = bytes([0])
ACK = bytes([0])
SYN_ACK = bytes([1])
PKG_BEGIN = 0xBE
PKG_END = 0xEF
A_BIT = 1
B_BIT = 2

uart = UART(baudrate=9600, tx=board.UART_TX2, rx=board.UART_RX2, bits=8, parity=None, stop=1, timeout=0.05)

def send_ready():
    uart.write(ACK)

print("Waiting for controller SYN")
timeout = 10
while uart.read(1) != SYN:
    if timeout > 0:
        timeout -= 1
        if timeout == 0:
            info_group = displayio.Group(scale=1, x=8, y=30)
            info_area = label.Label(terminalio.FONT, text="Press reset on\nMicrobit", color=0xFF0000)
            info_group.append(info_area)
            splash.append(info_group)

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

prev_time = time.monotonic()

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

    cur_time = time.monotonic()
    time_diff = cur_time - prev_time;
    prev_time = cur_time

    if btn_state & B_BIT or BTN_A.value == False:
        uart.write(bytes(b'A'))
    elif btn_state & A_BIT or BTN_B.value == False:
        uart.write(bytes(b'B'))
    elif BTN_X.value == False:
        uart.write(bytes(b'X'))
    elif BTN_Y.value == False:
        uart.write(bytes(b'Y'))

    # Controller sends a value between -1G and 1G for each axis. It's converted to a value between 0 and 0xFE, i.e. 254.
    # Thus zero is 127.
    acc_ctrl_x = (acc_ctrl_raw_x - 127) / 127
    # The accelerometer orientation on the Microbit is the opposite of the expected coordinate system.
    # Invert here and keep the  math easier to understand instead of moving parts around.
    acc_ctrl_y = (acc_ctrl_raw_y - 127) / -127

    # The Microbit is slightly angled on the board.
    acc_x = acc_ctrl_x * sin10 - acc_ctrl_y * cos10
    # Because of the orientation of the Y-axis, the acceleration is inverted.
    acc_y = -(acc_ctrl_x * cos10 + acc_ctrl_y * sin10)

    vel_x += acc_x * time_diff
    vel_y += acc_y * time_diff

    #print(f'acc_ctrl_raw {acc_ctrl_raw_x:3}, {acc_ctrl_raw_y:3} | acc_ctrl {acc_ctrl_x:11}, {acc_ctrl_y:11} | vel {vel_x:11}, {vel_y:11}')
    dx = vel_x * time_diff * px_per_m * physics_scale
    dy = vel_y * time_diff * px_per_m * physics_scale

    nx_tmp = pos_x + dx
    ny_tmp = pos_y + dy

    if nx_tmp < 0 or nx_tmp > 127:
        vel_x *= -bounce_factor
    if ny_tmp < 0 or ny_tmp > 159:
        vel_y *= -bounce_factor

    pos_x = max(min(nx_tmp, 127), 0)
    pos_y = max(min(ny_tmp, 159), 0)

    move_dot(int(pos_x), int(pos_y))

    # The time precision gets too low if we don't have any latency.
    time.sleep(0.05)
