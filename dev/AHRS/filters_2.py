from cmath import pi

import time
from mahony import *
import math
import ahrs
import numpy as np

x_a_offset = -0.01137564357366827
y_a_offset = 0.12418234651448756
z_a_offset = -0.04117713395608824

x_r_offset = 0.03201130448281042
y_r_offset = -0.01767855554417916
z_r_offset = -0.00030196657169167786

BOOST_TIME = 1.5

if True:
    
    yaw = np.array([])
    dT = np.array([])

    def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians

    with open('cleaned_data.txt', 'r', encoding='latin-1') as file:
        orientation = ahrs.filters.mahony.Mahony()
        Q = np.array([0., 1., 0., 1.])
        line = file.readline() #get rid of the header
        lines_read: int = 0
        #find first time stamp - !GETS RID OF FIRST LINE OF DATA!
        t_old: float = (int(file.readline().split(' ')[0]) / 1e+6)
        startLaunch = 0
        with open('quat.txt', 'w') as out:
            while line:
                line = file.readline()
                data = line.split(' ')
                if len(data) > 1: #replace this conditional
                    lines_read += 1
                    t_now: float = (int(data[0]) / 1e+6)
                    #get gyroscope measurements
                    if (float(data[13]) > 20):
                        startLaunch = int(data[0])

                    if (int(data[0]) - startLaunch < (BOOST_TIME * 1e6)):
                        gyro: list = [float(data[10]), 0, 0]
                        accel: list = [9.8, 0, 0]
                    else:
                        gyro: list = [float(data[10]) + x_r_offset, float(data[11]) + y_r_offset, float(data[12]) + z_r_offset]
                        accel: list = [float(data[13]) + x_a_offset, float(data[14]) + y_a_offset, float(data[15]) + z_a_offset]


                    #get accelerometer measurements
                    
                    orientation.Dt = t_now - t_old
                    Q = orientation.updateIMU(q = Q, gyr = np.array([gyro[0], gyro[1], gyro[2]]), acc=np.array([accel[0], accel[1], accel[2]]))
                    t_old = t_now
                    out.write(f'{Q[0]} {Q[1]} {Q[2]} {Q[3]}\n')
                    euler:list = euler_from_quaternion(Q[0], Q[1], Q[2], Q[3])
                    # print(f'{math.degrees(euler[0])} {math.degrees(euler[1])} {math.degrees(euler[2])}')
                    # print(lines_read)
                    dT = np.append(dT,float(data[0]))
                    yaw = np.append(yaw,float(data[1]))
                else:
                    print(f'Finished reading at line {lines_read}')
                    print(np.trapz(yaw,x=dT)%(2*pi))
                    print(yaw)
                    print("...")
                    print(dT)
