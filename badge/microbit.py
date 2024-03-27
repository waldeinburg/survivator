import board
import displayio
import terminalio
from adafruit_display_text import label
from busio import UART

SYN = bytes([0])
ACK = bytes([0])
SYN_ACK = bytes([1])
OK = bytes([0])
READY_FOR_INPUT = bytes([0])
PKG_BEGIN = 0xBE
PKG_END = 0xEF

GET_HIGHSCORE = bytes([1])
PUT_HIGHSCORE = bytes([2])
# 4 bytes are enough for a score of 25 days.
HIGHSCORE_SIZE = 4
HIGHSCORE_ORDER = 'big'

uart = None

# Input is special. We don't want to ask for input, then wait. Instead, ask for input immediately.
# If another command is wanted then first read and discard input.

def send_ready_for_input():
    uart.write(READY_FOR_INPUT)


def init(display):
    global uart
    uart = UART(baudrate=9600, tx=board.UART_TX2, rx=board.UART_RX2, bits=8, parity=None, stop=1, timeout=0.05)

    print("Waiting for controller SYN")
    timeout = 10
    info_group = None
    while uart.read(1) != SYN:
        if timeout > 0:
            timeout -= 1
            if timeout == 0:
                info_group = displayio.Group(x=8, y=30)
                info_area = label.Label(terminalio.FONT, text="Press reset on\nMicrobit", color=0xFF0000)
                info_group.append(info_area)
                display.show(info_group)
                display.refresh()

    print("Received SYN")
    uart.write(ACK)
    while uart.read(1) != SYN_ACK:
        print("Waiting for controller SYN-ACK")
    print("Received SYN-ACK")
    send_ready_for_input()


def read_value_or_reset(value):
    b = uart.read(1)
    if b is None or b[0] != value:
        print('b', b)
        uart.reset_input_buffer()
        return False
    return True


def read_package(size):
    if not read_value_or_reset(PKG_BEGIN):
        return None
    b = uart.read(size + 1)
    if b is None:
        return None

    if len(b) != size + 1 or b[-1] != PKG_END:
        uart.reset_input_buffer()
        return None

    return b[:-1]


def read_input():
    return read_package(3)


def get_input():
    while True:
        p = read_input()
        send_ready_for_input()
        if p is None:
            continue
        return p


def send_command(command, pkg_data, answer_size):
    # Discard input.
    read_input()
    p = None
    while p is None:
        print('command', command)
        uart.write(command)
        # If we don't receive OK, then try again immediately.
        if pkg_data is not None:
            print('expect OK')
            if not read_value_or_reset(OK):
                continue
            print('write data', pkg_data)
            uart.write(PKG_BEGIN)
            uart.write(pkg_data)
            uart.write(PKG_END)
        if answer_size == 0:
            print('expect OK')
            if not read_value_or_reset(OK):
                continue
            p = True
            break
        else:
            print('expect data')
            p = read_package(answer_size)
    send_ready_for_input()
    return p



def get_highscore():
    return int.from_bytes(send_command(GET_HIGHSCORE, None, HIGHSCORE_SIZE), HIGHSCORE_ORDER)


def put_highscore(score):
    send_command(PUT_HIGHSCORE, score.to_bytes(HIGHSCORE_SIZE, HIGHSCORE_ORDER), 0)
