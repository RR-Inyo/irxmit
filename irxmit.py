#!/usr/bin/python3
# -*- coding: utf-8 -*-

# irxmit.py - A module to transmit IR remote control signal frames
# (c) 2021 @RR_Inyo
# Version 0.10
# Released under the MIT license.
# https://opensource.org/licenses/mit-license.php

# This program currently supports the AEHA and the NEC formats only.

import pigpio

# For debugging
DEBUG = True
SINGLE_WAVE = False

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
        self.__pi = pigpio.pi(self.__host)
        self.__pi.set_mode(self.__pin, pigpio.OUTPUT)
        if DEBUG:
            print(f'A pigpio handler on {self.__host} obtained...')
            print(f'Maximum possible size of a waveform in DMA control blocks: {self.__pi.wave_get_max_cbs()}')
            print(f'Maximum possible size of a waveform in microseconds: {self.__pi.wave_get_max_micros()}')
            print(f'Maximum possible size of a waveform in pulses: {self.__pi.wave_get_max_cbs()}')

        # Define IR subcarrier and frame synthesis parameters
        # AEHA format
        if format == 'AEHA':
            self.__T_CARRIER = 26       # [microsec], carrier period
            self.__MARK_CYCLES = 17     # [cycles], number of carrier cycles in a mark/light
            self.__MARK_OFF = 3         # 'Off' (space/dark) time length relative to 'on' (light) length if '1'
            self.__T_FRAME_MAX = 0.13   # [s], expected maximum AEHA-format IR frame length
            self.__N_LEADER_ON = 8      # 'On' (mark/light) time units of the leader
            self.__N_LEADER_OFF = 4     # 'Off' (space/dark) time units of the leader

        # NEC format
        elif format == 'NEC':
            self.__T_CARRIER = 26       # [microsec], carrier period
            self.__MARK_CYCLES = 22     # [cycles], number of carrier cycles in a mark/light
            self.__MARK_OFF = 3         # 'Off' (space/dark) time length relative to 'on' (light) length if '1'
            self.__T_FRAME_MAX = 0.108  # [s], expected maximum AEHA-format IR frame length
            self.__N_LEADER_ON = 16     # 'On' (mark/light) time units of the leader
            self.__N_LEADER_OFF = 8     # 'Off' (space/dark) time units of the leader

        # Raise exception if unknown format is specified
        else:
            raise Exception('Unknown format specified.')

        if DEBUG: print(f'{format} format specified...')

        # Create waveform elements
        self.__synthesize_elements()

    # Destructor
    def __del__(self):
        # Release the pigpio
        self.__pi.stop()

    # Function to synthesize the AEHA-format IR frame as a chain of pigpio waveforms
    # For reuse of the waveform for marks and spaces to construct the chain of waveforms
    def __synthesize_elements(self):
        # Generate waveforms as frame elements as follows
        # - Leader
        # - Data '0', mark: T, space: T
        # - Data '1', mark: T, space: 3T
        # - Trailer

        # Clear wave
        self.__pi.wave_clear()

        # Generate waveform of leader
        wb = []
        for i in range(0, self.__MARK_CYCLES * self.__N_LEADER_ON):
            wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
            wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER // 2))
        wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES * self.__N_LEADER_OFF))
        self.__pi.wave_add_generic(wb)
        self.__wave_leader = self.__pi.wave_create()
        if DEBUG: print('Waveform for leader pulses created')

        # Generate waveform of Data '0'
        wb = []
        for i in range(0, self.__MARK_CYCLES):
            wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
            wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER // 2))
        wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES))
        self.__pi.wave_add_generic(wb)
        self.__wave_data_0 = self.__pi.wave_create()
        if DEBUG: print('Waveform for data \'0\' created')

        # Generate waveform of Data '1'
        wb = []
        for i in range(0, self.__MARK_CYCLES):
            wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
            wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER // 2))
        wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES * self.__MARK_OFF))
        self.__pi.wave_add_generic(wb)
        self.__wave_data_1 = self.__pi.wave_create()
        if DEBUG: print('Waveform for data \'1\' created')

        # Generate waveform of trailer
        wb = []
        for i in range(0, self.__MARK_CYCLES):
            wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
            wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER // 2))
        wb.append(pigpio.pulse(0, 1 << self.__pin, 8000 - self.__T_CARRIER * self.__MARK_CYCLES))
        self.__pi.wave_add_generic(wb)
        self.__wave_trailer = self.__pi.wave_create()
        if DEBUG: print('Waveform for trailer created')

    # Function to create LSB-first bitstream
    # Two frames can be connected with a '++' so that a leader pulse will be added therebetween in __synthesize() method.
    @classmethod
    def __get_bitstream(cls, s):
        bits = ''
        for i in range(0, len(s) // 2):
            byte = s[i * 2: i * 2 + 2]
            if byte == '++':
                bits += '+'
            else:
                bits_MSB_first = f'{int(byte, 16):08b}'
                bits += bits_MSB_first[::-1]
        if DEBUG: print(f'A bitstream of {bits} obtained...')
        return bits

    # Function to synthesize the AEHA-format IR frame as a single pigpio waveform
    # CAUTION: This method is obsolete and results in an error if the number of pulse objects exceeds 5,460.
    def __synthesize_single(self, bits):
        # Define wave buffer
        wb = []

        # Synthesize the leader pulses, mark: 8T, space: 4T
        # Mark, with the 38-kHz carrier
        for i in range(0, self.__MARK_CYCLES * self.__N_LEADER_ON):
            wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
            wb.append(pigpio.pulse(0, 1 << self.__pin,  self.__T_CARRIER // 2))
        # Space
        wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES * self.__N_LEADER_OFF))
        if DEBUG: print ('A pigpio waveform of leader pulses synthesized...')

        # Synthesize the data pulses
        for bit in bits:
            # Mark, for T, with the 38-kHz carrier
            for i in range(0, self.__MARK_CYCLES):
                wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
                wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER // 2))
            # Space, for T if bit is '0'
            if bit == '0':
                wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES))
            # Space, for 3T if bit is '1'
            elif bit == '1':
                wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER * self.__MARK_CYCLES * self.__MARK_OFF))
        if DEBUG: print ('A pigpio waveform of data pulses synthesized...')

        # Synthesize the trailer
        # Mark, for T, with the 38-kHz carrier
        for i in range(0, self.__MARK_CYCLES):
            wb.append(pigpio.pulse(1 << self.__pin, 0, self.__T_CARRIER // 2))
            wb.append(pigpio.pulse(0, 1 << self.__pin, self.__T_CARRIER // 2))
        # Space, for 8 ms - T
        wb.append(pigpio.pulse(0, 1 << self.__pin, 8000 - self.__T_CARRIER * self.__MARK_CYCLES))
        if DEBUG:
            print('A pigpio waveform of trailer pulses synthesized...')

        # Create a waveform based on the list of pulses
        self.__pi.wave_clear()
        self.__pi.wave_add_generic(wb)
        wave = self.__pi.wave_create()
        if DEBUG:
            print(f'A pigpio wave_id = {wave} obtained...')
            print(f'Length of waveform in DMA control blocks: {self.__pi.wave_get_cbs()}/{self.__pi.wave_get_max_cbs()}')
            print(f'Length of the waveform in microseconds: {self.__pi.wave_get_micros()}/{self.__pi.wave_get_max_micros()}')
            print(f'Length of the waveform in number of pulses: {self.__pi.wave_get_pulses()}/{self.__pi.wave_get_max_pulses()}')

        # Create and return wavechain as a list of wave_id although there is only a single element
        wc = [wave]
        return wc

    # Function to synthesize frame as a wavechain consisting of wave elements created in __synthesize_elements() method
    def __synthesize(self, bits):
        # Create empty wavechain
        wc = []

        # Append leader
        wc.append(self.__wave_leader)

        # Append data
        # If there is a '+' in the input string, a leader pulse is added to directly connect frames.
        for bit in bits:
            if bit == '0':
                wc.append(self.__wave_data_0)
            if bit == '1':
                wc.append(self.__wave_data_1)
            if bit == '+':
                wc.append(self.__wave_leader)

        # Append trailer
        wc.append(self.__wave_trailer)
        if DEBUG: print(f'Wavechain generated {wc}')

        return wc

    # Function to send an AEHA-format IR signal
    def send(self, s):
        if DEBUG: print(f'Creating a bitstream from the hexadecimal string data {s}...')
        bits = self.__get_bitstream(s)

        if SINGLE_WAVE:
            if DEBUG: print('Synthesizing the frame as a single wave...')
            wc = self.__synthesize_single(bits)
        else:
            if DEBUG: print('Synthesizing the frame as a wavechain with mutiple waves...')
            wc = self.__synthesize(bits)

        if DEBUG: print(f'Sending the pigpio wavechain on GPIO{self.__pin} pin...')
        self.__pi.wave_chain(wc)

    def is_busy(self):
        return self.__pi.wave_tx_busy()

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
    ir.send(sigs[0])

    # Wait for 10 seconds
    time.sleep(10)

    # Go back to normal mode (on)
    ir.send(sigs[1])

    # Wait for 10 seconds again
    time.sleep(10)

    # Full brightness!
    ir.send(sigs[2])

    # Release the pigpio after transmission
    while ir.is_busy():
        time.sleep(T_MAX)
    del ir
