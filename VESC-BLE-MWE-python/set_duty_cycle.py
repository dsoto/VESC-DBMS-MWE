# adapted from the Adafruit BLE python library examples
# see repo for installation instructions https://github.com/adafruit/Adafruit_Python_BluefruitLE

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART
import time

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.
def main():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        device = UART.find_device()
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print(device.name)
    print('Connecting to device...')
    # how do I connect to a specific device (out of my two?)
    device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                      # to change the timeout.

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        print('Discovering services...')
        UART.discover(device)

        # Once service discovery is complete create an instance of the service
        # and start interacting with it.
        uart = UART(device)

        # Now wait up to one minute to receive data from the device.
        print('Waiting up to 60 seconds to receive data from the device...')

        while True:
            # Write a string to the TX characteristic.
            message_string = create_packet()
            # we send a regular VESC packet of bytes over the BLE UART 
            uart.write(message_string)
            print('write complete')
            time.sleep(4.0)

    finally:
        # Make sure device is disconnected on exit.
        device.disconnect()

def create_packet():
    # this creates the packet for a set duty cycle command
    
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

    return packet


# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
