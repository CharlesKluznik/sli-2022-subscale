"""File containing utility functions used elsewhere in the payload.
"""

import math
import serial
import sys
import os
import numpy as np
from time import sleep
from datetime import datetime
import shutil

def euler_from_quaternion(x: float, y: float, z: float, w: float):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/

    Parameters:
    x, y, z, w (float) : components of quaternion
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

def log_teensy(port: str):
    with serial.Serial(port, baudrate=115200, timeout=10) as ser:
        print(f'Serial connected.', flush=True)
        with open(os.path.join(sys.path[0], 'serial.txt'), 'w') as out:
            print(f'Serial file opened.', flush=True)
            ser.flushInput()
            line = ser.readline().decode("utf-8").strip()
            while (line != "end"):
                print(f'{line}', flush=True)
                out.write(f'{line}\n')
                line = ser.readline().decode("utf-8").strip()
            print('Serial logging done.', flush=True)

def get_timestamp() -> str:
    """Returns timestamp in Month/Day/Year:Hour:Minute:Second format"""
    return datetime.now().strftime('%D:%H:%M:%S')

def clean_data(fName: str):
    MAX_LONG = 2147483647
    overflowed = 0
    PRESSURE_CUTOFF = 600
    SECS_BEFORE_APOGEE = 20
    SECS_AFTER_APOGEE = 150
    data = np.loadtxt(fName, skiprows=10, dtype=float)
    barom = data[:, 1]
    apogee_index = np.where(barom==min(barom))[0][0]
    lines_written = 0
    last_t = 0
    with open(fName, 'r') as inFile:
        with open(os.path.join(sys.path[0], 'cleaned_data.txt'), 'w') as outFile:
            for _ in range(10):
                #remove junk lines
                line = inFile.readline()
            while line:
                line = inFile.readline()
                if len(line) > 0:
                    tokens = line.split(' ')
                    tokens[0] = int(tokens[0])
                    #detect overflow
                    if tokens[0] < 0 and last_t > 0:
                        overflowed += 1
                        print("Overflowed!")
                    last_t = tokens[0]
                    tokens[0] = tokens[0] + overflowed * MAX_LONG;
                    #get gyroscope measurements
                    gyro1: list = [float(tokens[3]), float(tokens[4]), float(tokens[5])]
                    gyro2: list = [float(tokens[11]), float(tokens[12]), float(tokens[13])]
                    gyro: list = [((gyro1[0] + gyro2[0]) /2), ((gyro1[1] + gyro2[1]) /2), ((gyro1[2] + gyro2[2]) /2)]
                    #get accelerometer measurements
                    accel1: list = [float(tokens[6]), float(tokens[7]), float(tokens[8])]
                    accel2: list = [float(tokens[14]), float(tokens[15]), float(tokens[16])]
                    accel: list = [((accel1[0] + accel2[0]) /2), ((accel1[1] + accel2[1]) /2), ((accel1[2] + accel2[2]) /2)]
                    #get barometer measurements
                    baro: list = [((float(tokens[1]) + float(tokens[9])) / 2), ((float(tokens[2]) + float(tokens[10])) / 2)]
                    
                    if lines_written == 0:
                        launchpad_baro = baro[0]
                        
                    if (data[apogee_index][0] - (SECS_BEFORE_APOGEE * 1e6) < float(tokens[0]) 
                        and float(tokens[0]) < data[apogee_index][0] + (SECS_AFTER_APOGEE * 1e6) 
                        and not ('�' in line) ):
                        if (baro[0] > launchpad_baro - PRESSURE_CUTOFF and float(tokens[0]) > data[apogee_index][0]): line = False    
                        outFile.write(f'{tokens[0]} {gyro[0]} {gyro[1]} {gyro[2]} {accel[0]} {accel[1]} {accel[2]} {baro[0]} {baro[1]}\n')
                        lines_written+=1

def copy_logs():
    ts = datetime.now().strftime('%m-%d-%Y-%H-%M-%S')
    shutil.copyfile(os.path.join(sys.path[0], 'payload_log.txt'),os.path.join(sys.path[0], 'logs', f'payload_log-{ts}.txt'))
    shutil.copyfile(os.path.join(sys.path[0], 'cleaned_data.txt'),os.path.join(sys.path[0], 'logs', f'cleaned_data-{ts}.txt'))
    shutil.copyfile(os.path.join(sys.path[0], 'serial.txt'),os.path.join(sys.path[0], 'logs', f'serial-{ts}.txt'))
    shutil.copyfile(os.path.join(sys.path[0], 'quat.txt'),os.path.join(sys.path[0], 'logs', f'quat-{ts}.txt'))


