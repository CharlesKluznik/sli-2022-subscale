"""File containing functions that are used to filter raw data from the payload reference frame and generate an orientation estimate in the world reference frame.
"""
import ahrs
import numpy as np
from util import *
import traceback

#accelerometer offsets
x_a_offset = -0.01137564357366827
y_a_offset = 0.12418234651448756
z_a_offset = -0.04117713395608824

x_r_offset = 0.03201130448281042
y_r_offset = -0.01767855554417916
z_r_offset = -0.00030196657169167786

BOOST_TIME = 1.5


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
                            if (float(data[13]) > 20):
                                startLaunch = int(data[0])

                            if (int(data[0]) - startLaunch < (BOOST_TIME * 1e6)):
                                gyro: list = [float(data[10]), 0, 0]
                                accel: list = [float(data[13]), 0, 0]
                            else:
                                gyro: list = [float(data[10]) + x_r_offset, float(data[11]) + y_r_offset, float(data[12]) + z_r_offset]
                                accel: list = [float(data[13]) + x_a_offset, float(data[14]) + y_a_offset, float(data[15]) + z_a_offset]
                            orientation.Dt = t_now - t_old
                            Q = orientation.updateIMU(q = Q, gyr = np.array([gyro[0]+x_r_offset, gyro[1]+y_r_offset, gyro[2]+z_r_offset]), acc=np.array([accel[0]+z_a_offset, accel[1]+y_a_offset, accel[2]+z_a_offset]))
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