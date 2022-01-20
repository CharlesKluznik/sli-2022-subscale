from mahony import *
import os
if __name__ == "__main__":
    ahrs: AHRS = AHRS()
    with open('data.txt', 'r') as file:
        line = file.readline() #get rid of the header
        #find first time stamp - !GETS RID OF FIRST LINE OF DATA!
        t_old: float = (int(file.readline().split(' ')[0]) / 1e+9)
        os.remove('quat.txt')
        with open('quat.txt', 'w') as out:
            while line:
                line = file.readline()
                data = line.split(' ')
                t_now: float = (int(data[0]) / 1e+9)
                #get gyroscope measurements
                gyro: list = [float(data[1]), float(data[2]), float(data[3])]
                #get accelerometer measurements
                accel: list = [float(data[4]), float(data[5]), float(data[6])]
                ahrs.filter_update(gyro[0], gyro[1], gyro[2], accel[0], accel[1], accel[2], (t_now - t_old) * 100)
                #ahrs.filter_update(0.001, 0.001, 0.001, -.001, -.001, -9.7, 0.1)
                t_old = t_now
                out.write(f'{ahrs.SEq_1} {ahrs.SEq_2} {ahrs.SEq_3} {ahrs.SEq_4}\n')