"""Main file to be executed by payload. Manages the entire RaspberryPi portion of data collection, processing, and output.
"""
from util import *
from filters import *
from comm import *
import sys
import os
from time import sleep

sys.stdout = open(os.path.join(sys.path[0], 'payload_log.txt'), 'w')
sys.stderr = sys.stdout

SERIAL_PORT: str = '/dev/ttyACM0'

if (__name__ == "__main__"):
    print(f'{get_timestamp()} RPi Online.\n')
    #initialize lora radio and send a hearbeat
    lora_init()
    lora_hearbeat()

    #wait for serial port
    sleep(5)
    #log teensy serial data to file
    print(f'{get_timestamp()} Begin Serial Logging.')
    log_teensy(SERIAL_PORT)
    print(f'{get_timestamp()} End Serial Logging.')
    lora_hearbeat()

    #clean serial data
    print(f'{get_timestamp()} Begin Cleaning Data.')
    clean_data(os.path.join(sys.path[0], 'serial.txt'))
    print(f'{get_timestamp()} End Cleaning Data.')
    lora_hearbeat()

    #process flight data and generate output quaternions
    print(f'{get_timestamp()} Begin Orientation Estimate.')
    process_orientation(input=os.path.join(sys.path[0], 'cleaned_data.txt'), verbose=False)       
    print(f'{get_timestamp()} End Orientation Estimate.')
    lora_hearbeat()

    #generate position estimate
    print(f'{get_timestamp()} Begin Position Estimate.') 
    coordinate: Tuple[str, str] = process_position(os.path.join(sys.path[0], 'cleaned_data.txt'))
    print(f'{get_timestamp()} End Position Estimate.')
    lora_hearbeat()

    #transmit orientation via radio
    print(f'{get_timestamp()} RPi Finished. Transmitting coordinate.')

    while True:
        #transmit position estimate
        lora_transmit(f'X: {coordinate[0]}, Y: {coordinate[1]}')
        sleep(0.5)
