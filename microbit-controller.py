from microbit import *
import utime
import math

def now():
    return utime.ticks_us()


def digits(n):
    return int(math.log(n, 10)) + 1


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

timer_running = False
timer_tick = now()
timer_duration = 0
timer_visible = False
timer_next_display = 0


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
    if v == ACK:
        send_input_state()
    elif v == TIMER_START:
        timer_running = True
        timer_tick = now()
    elif v == TIMER_STOP:
        timer_running = False
    elif v == TIMER_RESET:
        timer_duration = 0
        timer_next_display = 0
        timer_tick = now()
    elif v == TIMER_SHOW:
        timer_visible = True
        timer_next_display = timer_duration
    elif v == TIMER_HIDE:
        timer_visible = False
        
    if timer_running:
        n = now()
        if utime.ticks_diff(n, timer_tick) >= 1_000_000:
            timer_duration += 1
            timer_tick = n
            # Approx. 1 sec. per digit is needed
            if timer_visible and timer_duration >= timer_next_display:
                timer_next_display = timer_duration + digits(timer_duration)
                display.scroll(timer_duration,
                               loop=False,
                               wait=False)

