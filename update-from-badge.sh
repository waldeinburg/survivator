#!/usr/bin/env bash
cd "${0%/*}"
rsync -avu --delete --exclude /boot_out.txt --exclude '/.*' /media/$USER/CIRCUITPY/ badge/
