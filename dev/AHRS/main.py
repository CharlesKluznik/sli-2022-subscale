"""Main file to be executed by payload. Manages the entire RaspberryPi portion of data collection, processing, and output.
"""
from util import *
from filters import *

if (__name__ == "__main__"):
    
    #Idle until RPi is triggered
    print('Type \'Y\' for verbose output or nothing for normal output. Press <enter> to start.')
    verbose = False
    if (input().lower() == 'y'):
        verbose = True

    #TODO request data file from teensy
    
    #process flight data and generate output quaternions
    process_data(input='data_accel_cal.txt', verbose=verbose)       

    #transmit orientation via radio
    print(f'Execution finished!')
