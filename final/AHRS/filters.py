"""File containing functions that are used to filter raw data from the payload reference frame and generate an orientation estimate in the world reference frame.
"""
from typing import Tuple
import ahrs
import numpy as np
from util import *
import traceback
from string import ascii_lowercase

#accelerometer offsets
x_a_offset = -0.01137564357366827
y_a_offset = 0.12418234651448756
z_a_offset = -0.04117713395608824
#gyroscope offsets
x_r_offset = 0.03201130448281042
y_r_offset = -0.01767855554417916
z_r_offset = -0.00030196657169167786
#duration of boost phase
BOOST_TIME = 1.5

METERS_TO_FEET = 3.28084
alphabet = list(ascii_lowercase)[0:20]


def process_orientation(input:str, verbose: bool):
    """Processes raw data from the specified input file. Writes output orientations to quats.txt in quaternion format.
    Parameters:
    input (string) : name of the input file including .txt
    verbose (bool) : set to True for more verbose console output
    """
    try:
        with open(os.path.join(sys.path[0], input), 'r') as file:
            if (verbose): print('Data file successfully opened.')
            orientation = ahrs.filters.mahony.Mahony()
            Q = np.array([0., 1., 0., 1.])
            line = file.readline() #get rid of the header
            lines_read: int = 0
            #find first time stamp - !GETS RID OF FIRST LINE OF DATA!
            t_old: float = (int(file.readline().split(' ')[0]) / 1e+6) #convert microseconds to seconds
            start_launch: int = 0
            try:
                with open(os.path.join(sys.path[0], 'quat.txt'), 'w') as out:
                    if (verbose): print('Output file successfully opened')
                    while line:
                        line = file.readline()
                        data = line.split(' ')
                        if len(data) > 1: #check that the line of data has columns
                            lines_read += 1
                            t_now: float = (int(data[0]) / 1e+6) #convert microseconds to seconds
                            #get gyroscope measurements
                            if (float(data[4]) > 20):
                                start_launch = int(data[0])

                            if (int(data[0]) - start_launch < (BOOST_TIME * 1e6)):
                                gyro: list = [float(data[1]), 0, 0]
                                accel: list = [float(data[4]), 0, 0]
                            else:
                                gyro: list = [float(data[1]) + x_r_offset, float(data[2]) + y_r_offset, float(data[3]) + z_r_offset]
                                accel: list = [float(data[4]) + x_a_offset, float(data[5]) + y_a_offset, float(data[6]) + z_a_offset]
                            orientation.Dt = t_now - t_old
                            Q = orientation.updateIMU(q = Q, gyr = np.array([gyro[0]+x_r_offset, gyro[1]+y_r_offset, gyro[2]+z_r_offset]), acc=np.array([accel[0]+z_a_offset, accel[1]+y_a_offset, accel[2]+z_a_offset]))
                            t_old = t_now
                            out.write(f'{Q[0]} {Q[1]} {Q[2]} {Q[3]}\n') #write current quaternion to output file
                            if (verbose):  print_eulers(Q)
                            
                        else:
                            print(f'Finished reading at line {lines_read}.')
            except OSError as ex:
                print(f'Opening output file failed. Exception: {ex}')
                traceback.print_exc(ex)
            else:
                if (verbose): print(f'Finished writing quaternion values to file.')
    except OSError as ex:
        print(f'Opening input file failed. Exception: {ex}')
        traceback.print_exc(ex)

def process_position() -> Tuple[str, str, float, float]:

    """Processes orientation, acceleration, and time data to obtain estimated final coordinate.
    Inputs: Acceleration Data, Quaternions, Velocity Data (Outputted from this script)
    Returns: [x_box, y_box]
    """

    # -----------------1: IMPORT DATA---------------------------------------------------

    # aB = Linear Acceleration (Columns 4,5,6 in data.txt)
    # t = time (column 1 in data.txt)
    # Beta = quaternions (Columns 1,2,3,4)

    data = np.loadtxt(os.path.join(sys.path[0], 'cleaned_data.txt'), skiprows=1, dtype=float)  # Import data.txt file
    quats = np.loadtxt(os.path.join(sys.path[0], 'quat.txt'), dtype=float)

    t = data[:, 0] * 1e-6  # Time data (data.txt column 0)
    axB = data[:, 4] + x_a_offset# X coord Acc. data (data.txt column 3)
    ayB = data[:, 5] + y_a_offset
    azB = data[:, 6] + z_a_offset

    b0 = quats[:, 0]  # Quat 1 data (quat function column 3)
    b1 = quats[:, 1]
    b2 = quats[:, 2]
    b3 = quats[:, 3]

    barom = data[:, 8]
    start_altitude = barom[0]
    apogee_index = np.where(barom==min(barom))[0][0]
    print('apogee index:',apogee_index)

    # -----------------2: Convert Quaternions into rotation matrix---------------------------

    RBIarray = []

    for i in range(len(quats)):
        RBIarray.append( [[(b0[i]**2)+(b1[i]**2)-(b2[i]**2)-(b3[i]**2), 2*((b1[i]*b2[i])+(b0[i]*b3[i])), 2*((b1[i]*b3[i])-(b0[i]*b2[i]))],
                       [2*((b1[i]*b2[i])-(b0[i]*b3[i])), (b0[i]**2)-(b1[i]**2)+(b2[i]**2)-(b3[i]**2), 2*((b2[i]*b3[i])+(b0[i]*b1[i]))],
                       [2*((b1[i]*b3[i])+(b0[i]*b2[i])), 2*((b2[i]*b3[i])-(b0[i]*b1[i])), (b0[i]**2)-(b1[i]**2)-(b2[i]**2)+(b3[i]**2)]])

    RBIarray = np.array(RBIarray)
    # ----------------3: Convert Acc to Inertial Reference Frame----------------------------
    aB = []
    for i in range(len(quats)):
        aB.append([axB[i],ayB[i],azB[i]])
    aB = np.array(aB)
    aI = []  # Acc in Inertial Ref Frame (IRF)

    for i in range(len(quats)):
        aI.append( np.dot(np.linalg.inv(RBIarray[i]), np.transpose(aB[i]) )) # Acc in Inertial Ref Frame (IRF)
    aI = np.array(aI)

    for i in range(len(aI)):
        aI[i][2] -= 9.81


    # print(aI[1:10])

    # ----------------4: TrapZ integration of Inertial Acc to Inertial Vel----------------------
    vI = [[0,0,0]]

    for i in range(1,len(quats)):
        sumx = vI[i-1][0] + ((t[i] - t[i-1]) * (aI[i][0] + aI[i-1][0]) * 0.5)
        sumy = vI[i-1][1] + ((t[i] - t[i-1]) * (aI[i][1] + aI[i-1][1]) * 0.5)
        sumz = vI[i-1][2] + ((t[i] - t[i-1]) * (aI[i][2] + aI[i-1][2]) * 0.5)
        vI.append([sumx, sumy, sumz])
    vI = np.array(vI)

    print("final velocities:",vI[len(vI) - 1])

    # ----------------5: TrapZ integration of Inertial Vel to Inertial Pos----------------------
    
    dI = [[0,0,0]]
    sumx = sumy = sumz = 0
    z_max = z_max_line = 0
    j = 1

    while j < (len(quats)-1) and not (j>apogee_index and barom[j] >= start_altitude):
        sumx = dI[j-1][0] + ((t[j] - t[j-1]) * (vI[j][0] + vI[j-1][0]) * 0.5)
        sumy = dI[j-1][1] + ((t[j] - t[j-1]) * (vI[j][1] + vI[j-1][1]) * 0.5)
        sumz = dI[j-1][2] + ((t[j] - t[j-1]) * (vI[j][2] + vI[j-1][2]) * 0.5)
        dI.append([sumx, sumy, sumz])
        if (sumz > z_max): 
            z_max = sumz 
            z_max_line = j
        if (j==apogee_index): print("at lowest baro value, height reads {0:.2f}ft, line is {1}".format(sumz*METERS_TO_FEET, j))
        j+=1

    dI = np.array(dI)
    print("stopping at line", j)
    print("MAX Z: {0:.2f}ft at line {1}".format(z_max*METERS_TO_FEET, z_max_line))
    print("final displacements:",dI[len(dI)-1])

    # ---------------6: Conversion from final displacements to box coordinates--------------------------

    finalx = dI[len(dI)-1][0] * METERS_TO_FEET
    finaly = dI[len(dI)-1][1] * METERS_TO_FEET
    finalz = dI[len(dI)-1][2] * METERS_TO_FEET

    indexX = 10 + ( (int) (finalx/250))
    indexY = 10 - ( (int) (finaly/250))

    if (finalx < 0): indexX -= 1
    if (finaly > 0): indexY -= 1

    boxX = alphabet[indexX].upper()
    boxY = alphabet[indexY]

    print("Final Results:")
    print("X: {0:.2f}ft".format(finalx))
    print("Y: {0:.2f}ft".format(finaly))
    print("Z: {0:.2f}ft".format(finalz))
    print("Box: ({0}, {1})".format(boxX, boxY))
    return [boxX, boxY, finalx, finaly]


def print_eulers(Q: np.ndarray):
    """ Calculates euler angles from a given ndarray and prints them to the console.
    Parameters:
    Q (ndarray) : 4 element array containing the [x,y,z,w] components of a quaternion
    """
    euler:list = euler_from_quaternion(Q[0], Q[1], Q[2], Q[3])
    print(f'{math.degrees(euler[0])} {math.degrees(euler[1])} {math.degrees(euler[2])}')