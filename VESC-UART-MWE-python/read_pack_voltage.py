# uses GET_VALUES 0x04 command to read pack voltage from VESC
# this uses a USB to UART device

import time
import serial
import numpy as np
import sys

# set up serial connection using port from command line
port = sys.argv[1]
ser = serial.Serial(port=port, baudrate=115200, timeout=1)

start          = 0x02
payload_length = 0x01
command        = 0x04
crc_1          = 0x40
crc_2          = 0x84
end            = 0x03

value_packet = bytes([start, payload_length, command, crc_1, crc_2, end])

while (1):

    # send values command over serial port
    ser.write(value_packet)

    # wait a bit for response
    time.sleep(0.1)

    # receive packet from serial
    response = ser.read(ser.in_waiting)

    # pack voltage is sent as a 16-bit integer and scaled by 10
    pack_voltage = (response[29] << 8 | response[30]) / 1e1
    print(pack_voltage)

    # delay before loop
    time.sleep(1)
