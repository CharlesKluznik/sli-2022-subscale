"""File containing functions that are used to filter raw data from the payload reference frame and generate an orientation estimate in the world reference frame.
"""
import ahrs
import numpy as np
from util import *
import traceback

#accelerometer offsets
X_OFFSET: float = -0.0113756
Y_OFFSET: float = 0.1241823
Z_OFFSET: float = -0.0411771


def process_data(input:str, verbose: bool):
    """Processes raw data from the specified input file. Writes output orientations to quats.txt in quaternion format.

    Parameters:
    input (string) : name of the input file including .txt
    verbose (bool) : set to True for more verbose console output
    """
    try:
        with open(f'{__file__}\..\{input}', 'r') as file:
            if (verbose): print('Data file successfully opened.')
            orientation = ahrs.filters.mahony.Mahony()
            Q = np.array([0., 1., 0., 1.])
            line = file.readline() #get rid of the header
            lines_read: int = 0
            #find first time stamp - !GETS RID OF FIRST LINE OF DATA!
            t_old: float = (int(file.readline().split(' ')[0]) / 1e+6) #convert microseconds to seconds
            try:
                with open(f'{__file__}\..\quat.txt', 'w') as out:
                    if (verbose): print('Output file successfully opened')
                    while line:
                        line = file.readline()
                        data = line.split(' ')
                        if len(data) > 1: #check that the line of data has columns
                            lines_read += 1
                            t_now: float = (int(data[0]) / 1e+6) #convert microseconds to seconds
                            #get gyroscope measurements
                            gyro: list = [float(data[10]), float(data[11]), float(data[12])]
                            #get accelerometer measurements
                            accel: list = [float(data[13]), float(data[14]), float(data[15])]
                            orientation.Dt = t_now - t_old
                            Q = orientation.updateIMU(q = Q, gyr = np.array([gyro[0], gyro[1], gyro[2]]), acc=np.array([accel[0]+X_OFFSET, accel[1]+Y_OFFSET, accel[2]+Z_OFFSET]))
                            t_old = t_now
                            out.write(f'{Q[0]} {Q[1]} {Q[2]} {Q[3]}\n') #write current quaternion to output file
                            if (verbose):  print_eulers(Q)
                            
                        else:
                            print(f'Finished reading at line {lines_read}.')
            except OSError as ex:
                print(f'Opening output file failed. Exception: {ex.__class__}')
                traceback.print_exc(ex)
            else:
                if (verbose): print(f'Finished writing quaternion values to file.')
    except OSError as ex:
        print(f'Opening input file failed. Exception: {ex.__class__}')
        traceback.print_exc(ex)


def print_eulers(Q: np.ndarray):
    """ Calculates euler angles from a given ndarray and prints them to the console.

    Parameters:
    Q (ndarray) : 4 element array containing the [x,y,z,w] components of a quaternion
    """
    euler:list = euler_from_quaternion(Q[0], Q[1], Q[2], Q[3])
    print(f'{math.degrees(euler[0])} {math.degrees(euler[1])} {math.degrees(euler[2])}')