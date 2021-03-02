#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Test of turn on and off of the Verini television
# (c) 2021 @RR_Inyo

import irxmit
import time

# Define IR transmitter handler
TV_POWER = '06f901fe'
ir = irxmit.IRxmit(13, format = 'NEC')

# Transmit signal to turn on/off TV
print('Sending on/off signal to TV.')
ir.send(TV_POWER)

# Wait for 10 second
print('Waiting 10 seconds.')
time.sleep(10)

# Transmit signal to turn on/off TV again
print('Sending on/off signal to TV again.')
ir.send(TV_POWER)
