# Survivator

## Backstory

_Trapped in a dark area in Space (yes, I know, that's just how Space is, you get the point),
constantly being attacked by hostile ... stuff, how long will you survive (no, you can't just
escape, yes, I know it's Space but ... good grief, just let me put in the question mark and
finish)?_

## I don't want a backstory

Okay, sorry.

Survivator is a simple arcade game made for the
[BornHack 2022 Game On Badge](https://github.com/bornhack/badge2022) (disclaimer: I got the badge
as a birthday present) using a [micro:bit](https://microbit.org) to get motion control and for
saving high scores (because the CircuitPython system on the badge has a read-only file system).

## Setup

The code was written on a micro:bit V2 and the CircuitPython version preloaded on the badge.
I suppose micro:bit V1 will also work. The following steps should get the game running:

* Connect the following pins with wire:

| micro:bit | badge |
|-----------|-------|
| `1`       | `RX2` |
| `2`       | `TX2` |
| `3V`      | `VCC` |

* Use standoffs and screws to mount the micro:bit onto the badge, connecting `GND` on both
  devices and micro:bit pin `0` to badge pin `A2`. The latter will be unused technically, but the
  micro:bit will fit nicely and the angle will be right for what is assumed in the code.

* Use [python.microbit.org](https://python.microbit.org) to flash `microbit-controller.py` onto
  the micro:bit.

* Copy the contents of the `badge` folder to the badge.

## Playing the game

The aim is to survive as long as possible. The screen will display the current high score and time.

With a gradually decreasing interval you will be attacked by three types of enemies, each having a
different way to be handled:

* _Tilt_ the device to dodge the green beam!
* Use _button A on the micro:bit_ to fire your energy field at the right time when attacked by the
  evil but nice looking smiley rocket!
* Use _the four badge buttons_ to activate your water shields and _tilt_ to push the wall of fire
  out of the area!

Weapon and shields are only active for a limited time and must recharge for some hundred
milliseconds before being available again, so you can't just win by clicking constantly.

When you're dead, use _button B on the micro:bit_ to restart.
