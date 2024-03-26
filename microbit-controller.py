from microbit import *
import utime
import math

HIGHSCORE_FILENAME='highscore'

SYN = bytes([0])
ACK = bytes([0])
SYN_ACK = bytes([1])
OK = 0x0
PKG_BEGIN = 0xBE
PKG_END = 0xEF
READY_FOR_INPUT = bytes([0])
GET_HIGHSCORE = bytes([1])
PUT_HIGHSCORE = bytes([2])
HIGHSCORE_SIZE = 4
HIGHSCORE_ORDER = 'big'

A_BIT = 1
B_BIT = 2


def acc_byte(v):
    # Cut off at -1000 or 1000 (1 G), i.e. only assume tilt.
    # * plus to make a positive integer between 0 and 2000,
    # * divide to a number between 0 and 0xFE (not 0XFF, we need an even number
    #   to get -1G and 1G to be the same absolute value.
    # * round down.
    return int((min(max(v, -1000), 1000) + 1000) / 2000 * 0xFE)


def send_input_state():
    btn_state = 0
    if button_a.is_pressed():
        btn_state |= A_BIT
    if button_b.is_pressed():
        btn_state |= B_BIT
    acc_x = acc_byte(accelerometer.get_x())
    acc_y = acc_byte(accelerometer.get_y())
    uart.write(bytes([PKG_BEGIN,
                      btn_state,
                      acc_x,
                      acc_y,
                      PKG_END]))

highscore = 0
try:
    with open(HIGHSCORE_FILENAME, 'r') as f:
        highscore = int(f.read())
except OSError:
    with open(HIGHSCORE_FILENAME, 'w') as f:
        f.write('0')

uart.init(tx=pin1, rx=pin2)

warn_timeout = 20
while uart.read(1) != ACK:
    uart.write(SYN)
    sleep(100)
    if warn_timeout > 0:
        warn_timeout -= 1
        if warn_timeout == 0:
            display.show('*', wait=False)

uart.write(SYN_ACK)

# Ready!
display.scroll("Survivator", wait=False)


while True:
    v = uart.read(1)
    if v == READY_FOR_INPUT:
        send_input_state()
    elif v == GET_HIGHSCORE:
        begin = bytes([PKG_BEGIN])
        data = highscore.to_bytes(HIGHSCORE_SIZE, HIGHSCORE_ORDER)
        end = bytes([PKG_END])
        uart.write(begin + data + end)
    elif v == PUT_HIGHSCORE:
        # TODO
        uart.write(bytes(OK))
