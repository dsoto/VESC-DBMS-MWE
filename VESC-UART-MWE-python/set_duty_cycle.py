# sets duty cycle of motor
# shows creation of bytes for duty cycle
# shows computation of CRC value

import time
import serial
import sys

# set up serial connection using port from command line
port = sys.argv[1]
ser = serial.Serial(port=port, baudrate=115200, timeout=1)

# create four bytes for the duty cycle value
duty_cycle = 0.1
scaling = 1e5
duty_cycle_value = int(duty_cycle * scaling)
duty_cycle_value_byte_1 = duty_cycle_value >> 24 & 0xff
duty_cycle_value_byte_2 = duty_cycle_value >> 16 & 0xff
duty_cycle_value_byte_3 = duty_cycle_value >>  8 & 0xff
duty_cycle_value_byte_4 = duty_cycle_value >>  0 & 0xff

# define command bytes
start = 0x02
payload_length = 0x05          # five bytes for command and 4 bytes for duty cycle
command = 0x05                 # this code is in datatypes.h
stop = 0x03

# create checksum only on the payload bytes
import crc16
crc = crc16.crc16xmodem(bytes([command, 
                               duty_cycle_value_byte_1, 
                               duty_cycle_value_byte_2,
                               duty_cycle_value_byte_3,
                               duty_cycle_value_byte_4]))
crc_1 = crc >> 8
crc_2 = crc & 0x00ff

# assemble the entire packet according to VESC format
packet = bytes([start, payload_length, command, 
                duty_cycle_value_byte_1, duty_cycle_value_byte_2, duty_cycle_value_byte_3, duty_cycle_value_byte_4,
                crc_1, crc_2, stop])

while (1):

    # send packet for values
    ser.write(packet)

    # delay before loop
    time.sleep(4)
