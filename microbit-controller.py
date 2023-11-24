from microbit import *

display.scroll("42", wait=False)

def acc_byte(v):
    # Cut off at -1000 or 1000 (1 G),
    # plus to make a positive integer between 0 and 2000,
    # divide to a number between 0 and 0xFF,
    # round down.
    return int((min(max(v, -1000), 1000) + 1000) / 2000 * 0xFF)

uart.init(tx=pin1, rx=pin2)

ACK = bytes([0])
PKG_BEGIN = 0xBE
PKG_END = 0xEF
A_BIT = 1
B_BIT = 2

main_ready = False
while uart.read(1) != ACK:
    uart.write(bytes([0]))
    sleep(100)
uart.write(bytes([1]))
display.show('X', wait=False)

while True:
    v = uart.read(1)
    if v is not None:
        if v == ACK:
            main_ready = True
        else:
            display.scroll(str(v, 'ASCII'), loop=False, wait=False)
    if main_ready:
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
        main_ready = False

