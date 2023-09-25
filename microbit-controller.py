from microbit import *

display.scroll("FOO", wait=False)

uart.init(tx=pin2, rx=pin1)

A_PRESS = 1
A_RELEASE = 2
B_PRESS = 3
B_RELEASE = 4


def send_event(ev):
    uart.write(bytes([ev]))


class Button:
    def __init__(self, button, press_event, release_event):
        self.button = button
        self.press_event = press_event
        self.release_event = release_event
        self.pressed = False

    def check_state(self):
        if self.button.is_pressed() and not self.pressed:
            self.pressed = True
            send_event(self.press_event)
        elif not self.button.is_pressed() and self.pressed:
            self.pressed = False
            send_event(self.release_event)


btn_a = Button(button_a, A_PRESS, A_RELEASE)
btn_b = Button(button_b, B_PRESS, B_RELEASE)


while True:
    btn_a.check_state()
    btn_b.check_state()
