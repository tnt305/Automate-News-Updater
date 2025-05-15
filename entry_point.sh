#!/bin/bash
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99
python test.py
rm -f /tmp/.X99-lock

## Tempt