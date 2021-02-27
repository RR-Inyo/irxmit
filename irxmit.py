#!/usr/bin/python3
# -*- coding: utf-8 -*-

# irxmit.py - A module to transmit IR remote control signal frames
# (c) 2021 @RR_Inyo
# Released under the MIT license.
# https://opensource.org/licenses/mit-license.php

# This program currently supports the AEHA and the NEC formats only.

import pigpio

# For debugging
DEBUG = True

# Explanation on IR subcarrier and frame synthesis parameters:
#
# In the AEHA format, the subcarrier frequency shall be 33-40 kHz (typ. 38 kHz).
# The modulation unit, T, shall be 0.35-0.50 ms (typ. 0.425 ms).
# This program lets the carrier frequency be 38.4615 kHz, or the period be 0.026 ms.
# Making the modulation unit be 17 cycles of the subcarrier leads to T = 0.442 ms.
# The leader consists of 8T 'on' (light) and 4T 'off' (dark).
#
# In the NEC format, the subcarrier frequency shall be 38 kHz (I do not know tolerance).
# The modulation unit, T, shall be 0.562 ms (I do not know the tolerance).
# This program lets the carrier frequency be 38.4615 kHz, or the period be 0.026 ms.
# Making the modulation unit, T, be 22 cycles of the subcarrier leads to T = 0.572 ms (longer by 1.7%).
# The leader consists of 16T 'on' (light) and 8T 'off' (dark).

# Class of IR transmitter
class IRxmit():
    # Constructor
    def __init__(self, pin, host = '127.0.0.1', format = 'AEHA'):
        # Define private variables for pigpio
        self.__pin = pin
        self.__host = host

        # Get pigpio handler and set GPIO pin connected to IR LED(s) to output
        self.pi = pigpio.pi(self.__host)
        self.pi.set_mode(self.__pin, pigpio.OUTPUT)
        if DEBUG: print(f'A pigpio handler on {self.__host} obtained...')

        # Define IR subcarrier and frame synthesis parameters
        # AEHA format
        if format == 'AEHA':
            self.__T_CARRIER = 26       # [microsec], carrier period
            self.__MARK_CYCLES = 17     # [cycles], number of carrier cycles in a mark
            self.__MARK_OFF = 3         # 'Off' (dark) time length relative to 'on' (light) length if '1'
            self.__T_FRAME_MAX = 0.13   # [s], expected maximum AEHA-format IR frame length
            self.__T_LEADER_ON = 8      # 'On' (light) time of the leader
            self.__T_LEADER_OFF = 4     # 'Off' (dark) time of the leader

        # NEC format
        elif format == 'NEC':
            self.__T_CARRIER = 26       # [microsec], carrier period
            self.__MARK_CYCLES = 22     # [cycles], number of carrier cycles in a mark
            self.__MARK_OFF = 3         # 'Off' (dark) time length relative to 'on' (light) length if '1'
            self.__T_FRAME_MAX = 0.108  # [s], expected maximum AEHA-format IR frame length
            self.__T_LEADER_ON = 16     # 'On' (light) time of the leader
            self.__T_LEADER_OFF = 8     # 'Off' (dark) time of the leader

        # Raise exception if unknown format is specified
        else:
            raise Exception('Unknown format specified.')

        if DEBUG: print(f'{format} format specified...')

    # Destructor
    def __del__(self):
        # Release the pigpio
        self.pi.stop()

    # Function to create LSB-first bitstream
    @classmethod
    def get_bitstream(cls, s):
        bits = ''
        for i in range(0, len(s) // 2):
            byte = s[i * 2: i * 2 + 2]
            bits_MSB_first = f'{int(byte, 16):08b}'
            bits += bits_MSB_first[::-1]
        if DEBUG: print(f'A bitstream of {bits} obtained...')
        return bits

    # Function to synthesize the AEHA-format IR frame as pigpio waveform
    def synthesize_frame(self, bits):
        # Define wave buffer
        wb = []

        # Synthesize the leader pulses, on: 8T, off: 4T
        # On, with the 38-kHz carrier
        for i in range(0, self.__MARK_CYCLES * self.__T_LEADER_ON):
            wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
            wb.append(pigpio.pulse(0, 1 << self.__pin,  self.__T_CARRIER // 2))
        # Off
        wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES * self.__T_LEADER_OFF))
        if DEBUG: print ('A pigpio waveform of leader pulses synthesized...')

        # Synthesize the data pulses
        for bit in bits:
            # On pulse, for T, with the 38-kHz carrier
            for i in range(0, self.__MARK_CYCLES):
                wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
                wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER // 2))
            # Off pulse, for T if bit is '0'
            if bit == '0':
                wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES))
            # Off pulse, for 3T if bit is '1'
            elif bit == '1':
                wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES * self.__MARK_OFF))
        if DEBUG: print ('A pigpio waveform of data pulses synthesized...')

        # Synthesize the trailer
        # On pulse, for T, with the 38-kHz carrier
        for i in range(0, self.__MARK_CYCLES):
            wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
            wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER // 2))
        # Off pulse, for 8 ms - T
        wb.append(pigpio.pulse(0, 1 << self.__pin, 8000 - self.__T_CARRIER * self.__MARK_CYCLES))
        if DEBUG: print ('A pigpio waveform of trailer pulses synthesized...')

        # Create a waveform based on the list of pulses
        self.pi.wave_clear()
        self.pi.wave_add_generic(wb)
        wave = self.pi.wave_create()
        if DEBUG: print('A pigpio wave_id obtained...')

        return wave

    # Function to send an AEHA-format IR signal
    def send(self, s):
        if DEBUG: print(f'Creating a bitstream from the hexadecimal string data {s}...')
        bits = self.get_bitstream(s)

        if DEBUG: print(f'Synthesizing a pigpio waveform from the bitstream {bits}...')
        wave = self.synthesize_frame(bits)

        if DEBUG: print(f'Sending the pigpio waveform on GPIO{self.__pin} pin...')
        self.pi.wave_send_once(wave)

    def is_busy(self):
        return self.pi.wave_tx_busy()

# Test codes
if __name__ == '__main__':

    import time

    # Define wait while busy
    T_MAX = 0.2

    # Get an instance object of IRxmit class
    ir = IRxmit(13)

    # Define signal examples
    # MSB-first here, but shall be sent LSB-first.
    # Based on an LED ceiling lighing from Panasonic
    # sig[0]: Night mode
    # sig[1]: Power
    # sig[2]: Full
    sigs = ['2c52092e27', '2c52092d24', '2c52092c25']

    # Go to night mode
    ir.send(sig[0])

    # Wait for 10 seconds
    time.sleep(10)

    # Go back to normal mode (on)
    ir.send(sig[1])

    # Wait for 10 seconds again
    time.sleep(10)

    # Full brightness!
    ir.send(sig[2])

    # Release the pigpio after transmission
    while ir.is_busy():
        time.sleep(T_MAX)
    del ir
