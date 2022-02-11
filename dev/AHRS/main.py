import math
import ahrs
import numpy as np
from util import *
import traceback

if (__name__ == "__main__"):
    #accelerometer offsets
    X_OFFSET: float = -0.0113756
    Y_OFFSET: float = 0.1241823
    Z_OFFSET: float = -0.0411771
    #Idle until RPi is triggered
    print('Waiting for input, press <enter>')
    input()

    #TODO request data file from teensy
    
    #read in data and generate orientation
    try:
        with open(f'{__file__}\..\data_calibration.txt', 'r') as file:
            print('Data file successfully opened.')
            orientation = ahrs.filters.mahony.Mahony()
            Q = np.array([0., 1., 0., 1.])
            line = file.readline() #get rid of the header
            lines_read: int = 0
            #find first time stamp - !GETS RID OF FIRST LINE OF DATA!
            t_old: float = (int(file.readline().split(' ')[0]) / 1e+6)
            try:
                with open(f'{__file__}\..\quat.txt', 'w') as out:
                    print('Output file successfully opened')
                    while line:
                        line = file.readline()
                        data = line.split(' ')
                        if len(data) > 1: #replace this conditional
                            lines_read += 1
                            t_now: float = (int(data[0]) / 1e+6)
                            #get gyroscope measurements
                            gyro: list = [float(data[10]), float(data[11]), float(data[12])]
                            #get accelerometer measurements
                            accel: list = [float(data[13]), float(data[14]), float(data[15])]
                            orientation.Dt = t_now - t_old
                            Q = orientation.updateIMU(q = Q, gyr = np.array([gyro[0], gyro[1], gyro[2]]), acc=np.array([accel[0]+X_OFFSET, accel[1]+Y_OFFSET, accel[2]+Z_OFFSET]))
                            t_old = t_now
                            out.write(f'{Q[0]} {Q[1]} {Q[2]} {Q[3]}\n')
                            euler:list = euler_from_quaternion(Q[0], Q[1], Q[2], Q[3])
                            #print(f'{math.degrees(euler[0])} {math.degrees(euler[1])} {math.degrees(euler[2])}')
                            
                        else:
                            print(f'Finished reading at line {lines_read}.')
                            print(f'Finished writing quaternion values to file.')
            except OSError as ex:
                print(f'Opening output file failed. Exception: {ex.__class__}')
                traceback.print_exc(ex)
    except OSError as ex:
        print(f'Opening input file failed. Exception: {ex.__class__}')
        traceback.print_exc(ex)
            

    #transmit orientation via radio
    print(f'Execution finished!')
