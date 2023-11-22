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
# Setting upper left pixel shows that the first visible point is indeed 2x1.
display = ST7735R(display_bus, width=128, height=160, bgr=True, colstart=2, rowstart=1, backlight_pin=board.PWM0, brightness=0.5)

color_bitmap = displayio.Bitmap(128, 160, 2)
color_palette = displayio.Palette(2)
color_palette[0] = 0x000000
color_palette[1] = 0xFF0000
color_bitmap[0] = 1
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash = displayio.Group()
splash.append(bg_sprite)
display.show(splash)

while True:
    time.sleep(1)

def DrawMenu(currentselected, paths):
    rim_bitmap = displayio.Bitmap(128, 160, 1)
    rim_palette = displayio.Palette(1)
    rim_palette[0] = 0x000000 #black
    rim_sprite = displayio.TileGrid(rim_bitmap, pixel_shader=rim_palette, x=0,  y=0)
    menu.append(rim_sprite)

    #bg_bitmap = displayio.Bitmap(118, 150, 1)
    #bg_palette = displayio.Palette(1)
    #bg_palette[0] = 0x000000 #Black

    #bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=5, y=5)
    #menu.append(bg_sprite)

    bh_colors = []
    bh_colors.append(0x004DFF)
    bh_colors.append(0x750787)
    bh_colors.append(0x008026)
    bh_colors.append(0xFFED00)
    bh_colors.append(0xFF8C00)
    bh_colors.append(0xE40303)

    # Draw a smaller colors
    for i in range(6):
        inner_bitmap = displayio.Bitmap(8, 8, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = bh_colors[i] # color
        inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=120, y=100+(i*8))
        menu.append(inner_sprite)

    it = 0
    for opt in paths:
        it+=1

        menu_text0_group = displayio.Group(scale=1, x=8, y=10*it)
        #print(it)
        if currentselected == it:
            menu_text0_area = label.Label(terminalio.FONT, text=opt, color=0xFFFFFF)
        else:
            menu_text0_area = label.Label(terminalio.FONT, text=opt, color=0x777777)
        menu_text0_group.append(menu_text0_area)
        menu.append(menu_text0_group)

    display.show(menu)

# Make the display context


selected = 1
menu = displayio.Group()

dir_path = r'apps/'

# list to store files
res = []

# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if isfile(join(dir_path, path)):
        res.append(path)

DrawMenu(selected, res)

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

    #if BTN_A.value == False:
    if (b is not None and (btn_state & B_BIT or acc_x > 0xA0)) or BTN_A.value == False:
        uart.write(bytes(b'A'))
        if selected == 1:
            pass
        else:
            selected-=1
            DrawMenu(selected, res)
            time.sleep(0.2)

    #if BTN_B.value == False:
    if (b is not None and (btn_state & A_BIT or acc_x < 0x5F)) or BTN_B.value == False:
        uart.write(bytes(b'B'))
        if selected == len(res):
            pass
        else:
            selected+=1
            DrawMenu(selected, res)
        time.sleep(0.2)

    if BTN_X.value == False or BTN_Y.value == False:
        try:
            exec(open(join(dir_path, res[selected-1])).read())
        except:
            pass
        DrawMenu(selected, res)
    pass
