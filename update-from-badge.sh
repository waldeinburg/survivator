#!/usr/bin/env bash
cd "${0%/*}"
rsync -avu --exclude /boot_out.txt --exclude '/.*' /media/$USER/CIRCUITPY/ badge/
