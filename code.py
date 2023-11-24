print("Starting ...")

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

def join(*xs):
    return '/'.join(x.rstrip('/') for x in xs)


def isfile(path):
    try:
        with open(path):
            pass
    except FileNotFoundError:
        return False
    else:
        return True

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

display_bus = displayio.FourWire(
	spi, command=tft_dc, chip_select=tft_cs, reset=board.D0
)

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

pos_x = 64
pos_y = 80

def set_pixel(x, y, c):
    color_bitmap[y * 128 + x] = c

# TODO: double-buffer
def move_dot(x, y):
    global pos_x, pos_y
    set_pixel(pos_x, pos_y, 0)
    set_pixel(x, y, 1)
    pos_x = x
    pos_y = y


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

while uart.read(1) != SYN:
    print("Waiting for controller SYN")
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

#uart.write(bytes(b'X'))

while True:
    btn_state = None
    acc_x = None
    acc_y = None
    while not got_pkg_begin():
        pass
    b = uart.read(4)
    if b is not None:
        if len(b) != 4 or b[3] != PKG_END:
            uart.reset_input_buffer()
            send_ready()
            continue
        send_ready()
        btn_state, acc_x, acc_y, _ = b

    dx = 0
    dy = 0

    if (b is not None and (btn_state & B_BIT or acc_x > 0xA0)) or BTN_A.value == False:
        dy = -1
    elif (b is not None and (btn_state & A_BIT or acc_x < 0x5F)) or BTN_B.value == False:
        dy = 1

    if b is not None and acc_y < 0x5F or BTN_X.value == False:
        dx = -1
    elif b is not None and acc_y > 0xA0 or BTN_Y.value == False:
        dx = 1

    nx = max(min(pos_x + dx, 127), 0)
    ny = max(min(pos_y + dy, 159), 0)
    move_dot(nx, ny)
