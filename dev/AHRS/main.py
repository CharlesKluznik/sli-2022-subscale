from mahony import *
import math
import ahrs
import numpy as np

if (__name__ == "__main__"):
    
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

    with open('data_calibration.txt', 'r') as file:
        orientation = ahrs.filters.mahony.Mahony()
        Q = np.array([0., 0., 0., 1.])
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
