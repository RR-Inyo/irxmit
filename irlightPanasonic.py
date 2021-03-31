#!/usr/bin/python3
# -*- conding: utf-8 -*-

# irlightPanasonic.py - IR remote control module for Panasonic ceiling lights
# (c) 2021 @RR_Inyo

DEBUG = False

# Class of Panasonic ceiling light
class IRlightPanasonic():
    # Define the signals for channel 1, 2, and 3
    __ON    = ['2c52092d24', '2c5209353c', '2c52093d34']
    __OFF   = ['2c52092f26', '2c5209373e', '2c52093f36']
    __FULL  = ['2c52092c25', '2c5209343d', '2c52093c35']
    __NIGHT = ['2c52092e27', '2c5209363f', '2c52093e37']
    __HIGH  = ['2c52092a23', '2c5209323b', '2c52093a33']
    __LOW   = ['2c52092b22', '2c5209333a', '2c52093b32']
    __WARM  = ['2c523991a8', '2c523995ac', '2c523999a0']
    __COOL  = ['2c523990a9', '2c523994ad', '2c523998a1']

    # Constructor
    def __init__(self, ir, ch = 1):
        # Set channel
        if ch in [1, 2, 3]:
            self.__ch = ch
        else:
            raise ValueError('Unknown channel specified. Choose 1, 2, or 3.')

        # Create IR remote control handler
        self.__ir = ir
        if DEBUG: print('IR remote controller handler obtained')

    
    # Destructor
    def __del__(self):
        del self.__ir

    # Turn on
    def on(self):
        if DEBUG: print(f'Turning on, Panasonic ceiling light on channel {self.__ch}')
        self.__ir.send(IRlightPanasonic.__ON[self.__ch - 1])

    # Turn off
    def off(self):
        if DEBUG: print(f'Turning off, Panasonic ceiling light on channel {self.__ch}')
        self.__ir.send(IRlightPanasonic.__OFF[self.__ch - 1])

    # Turn on at full brightness
    def full(self):
        if DEBUG: print(f'Turning on at full brightness, Panasonic ceiling light on channel {self.__ch}')
        self.__ir.send(IRlightPanasonic.__FULL[self.__ch - 1])

    # Night mode
    def night(self):
        if DEBUG: print(f'Changing to night mode, Panasonic ceiling light on channel {self.__ch}')
        self.__ir.send(IRlightPanasonic.__NIGHT[self.__ch - 1])

    # Brighter
    def high(self):
        if DEBUG: print(f'Making brigher, Panasonic ceiling light on channel {self.__ch}')
        self.__ir.send(IRlightPanasonic.__HIGH[self.__ch - 1])

    # Darker
    def low(self):
        if DEBUG: print(f'Making darker, Panasonic ceiling light on channel {self.__ch}')
        self.__ir.send(IRlightPanasonic.__LOW[self.__ch - 1])

    # Warmer
    def warm(self):
        if DEBUG: print(f'Making warmer in color, Panasonic ceiling light on channel {self.__ch}')
        self.__ir.send(IRlightPanasonic.__WARM[self.__ch - 1])

    # Cooler
    def cool(self):
        if DEBUG: print(f'Making cooler in color, Panasonic ceiling light on channel {self.__ch}')
        self.__ir.send(IRlightPanasonic.__COOL[self.__ch - 1])

# The main function, for testing purposes
def main():
    import time

    # Define the IR remote controller handler connected to GPIO13
    ir = irxmit.IRxmit(13)

    # Define the Panasonic ceiling light handler at channel 1
    l1 = IRlightPanasonic(ir, ch = 1)

    # Define the Panasonic ceiling light handler at channel 2
    l2 = IRlightPanasonic(ir, ch = 2)

    # Light 1 to night mode
    l1.night()

    # Wait for 10 seconds
    time.sleep(10)

    # Light 1 to normal mode (on)
    l1.on()

    # Wait for 10 seconds
    time.sleep(10)

    # Light 1 to full brightness
    l1.full()

    # Wait for 10 seconds
    time.sleep(10)

    # Light 1 to normal mode (on)
    l1.on()

    # Wait for 10 seconds
    time.sleep(10)
 
    # Light 2 to night mode
    l2.night()

    # Wait for 10 seconds
    time.sleep(10)

    # Light 2 to normal mode (on)
    l2.on()

    # Wait for 10 seconds
    time.sleep(10)

    # Light 2 to full brightness
    l2.full()

    # Wait for 10 seconds
    time.sleep(10)

    # Light 2 to normal mode (on)
    l2.on()

if __name__ == '__main__':
    import irxmit
    main()
