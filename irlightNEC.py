#!/usr/bin/python3
# -*- coding: utf-8 -*-

# irlightNEC.py - Example of controling an LED ceiling light from NEC
# (c) 2021 @RR_Inyo
# Released under the MIT license.
# https://opensource.org/licenses/mit-license.php

import irxmit
import time

# Class of NEC ceiling light
class lightNEC:
    FULL = '826da659'
    NIGHT = '826dbc43'
    OFF = '826dbe41'

    # Constructor
    def __init__(self, ir):
        # Define IR remote control handler
        self.ir = ir

    # Turn on light at full brightness
    def full(self):
        self.ir.send(lightNEC.FULL)

    # Go into night mode
    def night(self):
        self.ir.send(lightNEC.NIGHT)

    # Turn off
    def off(self):
        self.ir.send(lightNEC.OFF)

# The main function
def main():
    # Define the IR remote contoller handler
    # IR LEDs connected to GPIO13 through MOSFET
    # NEC format
    ir = irxmit.IRxmit(13, format = 'NEC')

    # Define the ceiling light handler
    l = lightNEC(ir)

    # Turn it off
    print('Turning the light off...')
    l.off()

    # Wait for 10 seconds
    time.sleep(10)

    # Go back to night mode (since this experiment is at night...)
    print('Going back to night mode...')
    l.night()

if __name__ == '__main__':
    main()
