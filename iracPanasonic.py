#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import time

# For debugging
DEBUG = False

# Encoding IR remote control signal for Panasonic air conditioners
# (c) 2020 @RR_Inyo

# Class of Panasonic air conditioner
class IRACPanasonic():
    # Class variables
    FRAME_1 = '0220e00400000006'    # First frame

    # Constructor
    def __init__(self, ir):
        # Define IR remote controler handler
        self.__ir = ir

        # Define default status
        # Heating in January, February, March, April, November, and December, by default
        # Cooling in May, June, July, August, September, and October, by default
        self.__power = False
        month = datetime.date.today().month
        if month in [1, 2, 3, 4, 11, 12]:
            self.__mode = 'heating'
            self.__temp = 21
        if month in [5, 6, 7, 8, 9, 10]:
            self.__mode = 'cooling'
            self.__temp = 24
        self.__louver = 15
        self.__wind = 'auto'

        if DEBUG:
            print(f'Mode: {self.__mode}')
            print(f'Temperature: {self.__temp} degree Celcius')
            print(f'Louver: {self.__louver}')
            print(f'Wind velocity: {self.__wind}')

    # Encode
    def __encode(self):
        # Second frame, first 5 bytes
        frame_2 = '0220e00400'

        # Second frame, 6th byte, mode and power
        # Mode
        if self.__mode == 'heating':
            byte_6h = '4'
        elif self.__mode == 'cooling':
            byte_6h ='3'
        elif self.__mode == 'drying':
            byte_6h = '2'
        else:
            raise ValueError('Unknown mode specified')

        # Power
        if self.__power:
            byte_6l = '1'
        else:
            byte_6l = '0'

        frame_2 += byte_6h + byte_6l

        # Second frame, 7th byte, temperature
        byte_7 = f'{0x20 + ((self.__temp - 16) << 1):x}'
        frame_2 += byte_7

        # Second frame, 8th byte
        frame_2 += '80'

        # Second frame, 9th byte
        # Wind velocity
        if self.__wind == 'auto':
            byte_9h = 'a'
        elif self.__wind in range(1, 4):
            byte_9h = f'{self.__wind:x}'
        elif self.__wind == 4:
            byte_9h = '7'

        # Louvre setting
        # Currently only 'f' is implemented.
        byte_9l = 'f'

        frame_2 += byte_9h + byte_9l

        # Second frame, 10th-18th bytes
        frame_2 += '000006600000800016'

        # Calculate checksum
        checksum = 0
        for i in range(0, len(frame_2) // 2):
            if DEBUG: print(f'Calculating checksum: byte No. {i}')
            checksum += int(frame_2[i * 2: i * 2 + 2], 16)
        checksum %= 256

        frame_2 += f'{checksum:02x}'

        if DEBUG:
            print(f'Checksum: {checksum}')
            print(f'Second frame encoded as {frame_2}')

        return frame_2

    # Send the command
    def __command(self, frame_2):

        if DEBUG:
            print(f'1st frame: {IRACPanasonic.FRAME_1}')
            print(f'2nd frame: {frame_2}')

        # Connecting the two frames
        frame = IRACPanasonic.FRAME_1 + '++' + frame_2

        # Send the data to the IR transmitter
        self.__ir.send(frame)

    # Turn on in heating mode:
    def on_heating(self, temp):
        # Set status
        self.__mode = 'heating'
        self.__power = True
        self.__temp = temp

        # For debugging, confirm status
        if DEBUG:
            print(f'Mode: {self.__mode}')
            print(f'Temperature: {self.__temp} degree Celcius')
            print(f'Louver: {self.__louver}')
            print(f'Wind velocity: {self.__wind}')

        # Encode frame
        frame_2 = self.__encode()

        # Send command
        self.__command(frame_2)

    # Turn on in cooling mode:
    def on_cooling(self, temp):
        # Set status
        self.__mode = 'cooling'
        self.__power = True
        self.__temp = temp

        # For debugging, confirm status
        if DEBUG:
            print(f'Mode: {self.__mode}')
            print(f'Temperature: {self.__temp} degree Celcius')
            print(f'Louver: {self.__louver}')
            print(f'Wind velocity: {self.__wind}')

        # Encode frame
        frame_2 = self.__encode()

        # Send command
        self.__command(frame_2)

    # Turn on in drying mode:
    def on_drying(self, temp):
        # Set status
        self.__mode = 'drying'
        self.__power = True
        self.__temp = temp

        # For debugging, confirm status
        if DEBUG:
            print(f'Mode: {self.__mode}')
            print(f'Temperature: {self.__temp} degree Celcius')
            print(f'Louver: {self.__louver}')
            print(f'Wind velocity: {self.__wind}')

        # Encode second frame
        frame_2 = self.__encode()

        # Send command
        self.__command(frame_2)

    # Turn off
    def off(self):
        self.__power = False

        # For debugging, confirm status
        if DEBUG:
            print(f'Mode: {self.__mode}')
            print(f'Temperature: {self.__temp} degree Celcius')
            print(f'Louver: {self.__louver}')
            print(f'Wind velocity: {self.__wind}')

        # Encode second frame
        frame_2 = self.__encode()

        # Send command
        self.__command(frame_2)

# The main function, for testing
def main():
    # Define the IRxmit handler, LEDs connected to GPIO13 through MOSFET, AEHA format
    ir = irxmit.IRxmit(13, format = 'AEHA')

    # Define the air conditioner handler
    ac = IRACPanasonic(ir)

    # Turn on the air conditioner in heating mode at 22 degree Celcius
    #ac.on_heating(22)
    ac.off()

if __name__ == '__main__':
    import irxmit
    main()
