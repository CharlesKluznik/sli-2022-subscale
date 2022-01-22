#modified from https://toptechboy.com/9-axis-imu-lesson-21-visualizing-3d-rotations-in-vpython-using-quaternions/ 
from vpython import *
from vpython.no_notebook import stop_server
from time import *
import numpy as np
import math
print("Starting...")

scene.range=5
scene.background=color.yellow
toRad=2*np.pi/360
toDeg=1/toRad
scene.forward=vector(-1,-1,-1)
 
scene.width=1200
scene.height=1080
 
xarrow=arrow(length=4, shaftwidth=.1, color=color.red,axis=vector(1,0,0))
yarrow=arrow(length=4, shaftwidth=.1, color=color.green,axis=vector(0,1,0))
zarrow=arrow(length=4, shaftwidth=.1, color=color.blue,axis=vector(0,0,1))
 
frontArrow=arrow(length=4,shaftwidth=.2,color=color.purple,axis=vector(1,0,0))
upArrow=arrow(length=1,shaftwidth=.2,color=color.magenta,axis=vector(0,1,0))
sideArrow=arrow(length=2,shaftwidth=.2,color=color.orange,axis=vector(0,0,1))

print("Reading data...")
with open(f'{__file__}/../quat.txt', 'r') as file:
    lines_read: int = 0
    data=file.readline().split(' ')
    while (len(data) > 1):
        lines_read += 1
        q0=float(data[0])
        q1=float(data[1])
        q2=float(data[2])
        q3=float(data[3])

        roll=-math.atan2(2*(q0*q1+q2*q3),1-2*(q1*q1+q2*q2))
        pitch=math.asin(2*(q0*q2-q3*q1))
        yaw=-math.atan2(2*(q0*q3+q1*q2),1-2*(q2*q2+q3*q3))-np.pi/2

        k=vector(cos(yaw)*cos(pitch), sin(pitch),sin(yaw)*cos(pitch))
        y=vector(0,1,0)
        s=cross(k,y)
        v=cross(s,k)
        vrot=v*cos(roll)+cross(k,v)*sin(roll)

        frontArrow.axis=-vrot
        sideArrow.axis=-cross(k,vrot)
        upArrow.axis=-k
        data=file.readline().split(' ')
        frontArrow.length = 4
        upArrow.length = 1
        sideArrow.length = 2
        print(lines_read)
        rate(150) #limit max fps to 200
    print(f'Finished on line {lines_read}')
stop_server()
