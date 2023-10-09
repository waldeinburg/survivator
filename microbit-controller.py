from microbit import *

display.scroll("42", wait=False)

def acc_byte(v):
    return int(min(v, 1000) / 1000 * 0xFF)

uart.init(tx=pin1, rx=pin2)

PKG_BEGIN = 0xBE
A_BIT = 1
B_BIT = 2
PKG_END = 0xEF

main_ready = False
while not uart.any():
    uart.write(bytes([0]))
    sleep(100)
uart.write(bytes([1]))

while True:
    v = uart.read(1)
    if v is not None:
        b = v[0]
        if b == 0:
            main_ready = True
        else:
            display.scroll(str(v, 'ASCII'), loop=False)
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
    sleep(100)
