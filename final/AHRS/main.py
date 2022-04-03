"""Main file to be executed by payload. Manages the entire RaspberryPi portion of data collection, processing, and output.
"""
from util import *
from filters import *
from comm import *
import sys
import os
from time import sleep

print('Payload init.\n', flush=True)
print(f'Time: {get_timestamp()}\n')
os.system('ls /dev/tty* >> ports.txt')
os.system('sudo date >> ports.txt')
sys.stdout = open(os.path.join(sys.path[0], 'payload_log.txt'), 'w')
sys.stderr = sys.stdout

SERIAL_PORT: str = '/dev/ttyACM0'

if (__name__ == "__main__"):
    print(f'\n{get_timestamp()} RPi Online.\n', flush=True)
    #initialize lora radio and send a hearbeat
    try:
        sleep(1)
        lora_init()
        sleep(1)
        lora_hearbeat()
    except Exception as ex:
        print(f'lorainit exception: {ex}')

    #log teensy serial data to file
    print(f'{get_timestamp()} Begin Serial Logging.', flush=True)
    try: log_teensy(SERIAL_PORT)
    except Exception as ex:
        print(f'log_teensy exception: {ex}', flush=True)
    print(f'{get_timestamp()} End Serial Logging.', flush=True)
    lora_hearbeat()

    #clean serial data
    print(f'{get_timestamp()} Begin Cleaning Data.', flush=True)
    try: clean_data(os.path.join(sys.path[0], 'serial.txt'))
    except Exception as ex:
        print(f'clean_data exception: {ex}')
    print(f'{get_timestamp()} End Cleaning Data.', flush=True)
    lora_hearbeat()

    #process flight data and generate output quaternions
    print(f'{get_timestamp()} Begin Orientation Estimate.', flush=True)
    try: process_orientation(input=os.path.join(sys.path[0], 'cleaned_data.txt'), verbose=False)
    except Exception as ex:
        print(f'processs_orientation exception: {ex}')
    print(f'{get_timestamp()} End Orientation Estimate.', flush=True)
    lora_hearbeat()

    #generate position estimate
    print(f'{get_timestamp()} Begin Position Estimate.', flush=True) 
    try: coordinate: Tuple[str, str, float, float] = process_position()
    except Exception as ex:
        print(f'process_position exception: {ex}')
    print(f'{get_timestamp()} End Position Estimate.', flush=True)
    lora_hearbeat()

    #transmit orientation via radio
    print(f'{get_timestamp()} RPi Finished. Transmitting coordinate.', flush=True)

    iterations: int = 0
    while True:
        iterations +=1
        if (iterations == 5):
            try: copy_logs()
            except Exception as ex:
                print(f'copy_logs exception: {ex}')
        else:
            #transmit position estimate
            lora_transmit(f'{coordinate[2]} {coordinate[3]} {coordinate[0]}{coordinate[1]}')
            print(f'Transmitted {get_timestamp()}', flush=True)
            sleep(0.5)
