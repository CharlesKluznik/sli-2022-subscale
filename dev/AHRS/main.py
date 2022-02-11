import math
import ahrs
import numpy as np
from util import *

if (__name__ == "__main__"):
    with open('data_subscale2.txt', 'r') as file:
        orientation = ahrs.filters.mahony.Mahony()
        Q = np.array([0., 1., 0., 1.])
        line = file.readline() #get rid of the header
        lines_read: int = 0
        #find first time stamp - !GETS RID OF FIRST LINE OF DATA!
        t_old: float = (int(file.readline().split(' ')[0]) / 1e+6)
        with open('quat.txt', 'w') as out:
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
                    Q = orientation.updateIMU(q = Q, gyr = np.array([gyro[0], gyro[1], gyro[2]]), acc=np.array([accel[0], accel[1], accel[2]]))
                    t_old = t_now
                    out.write(f'{Q[0]} {Q[1]} {Q[2]} {Q[3]}\n')
                    euler:list = euler_from_quaternion(Q[0], Q[1], Q[2], Q[3])
                    print(f'{math.degrees(euler[0])} {math.degrees(euler[1])} {math.degrees(euler[2])}')
                    
                else:
                    print(f'Finished reading at line {lines_read}')
                    print(f'Finished writing quaternion values to file.')
