import string
import numpy as np
import pandas as pd

x_a_offset = -0.01137564357366827
y_a_offset = 0.12418234651448756
z_a_offset = -0.04117713395608824

METERS_TO_FEET = 3.28084

alphabet = list(string.ascii_lowercase)[0:20]

def quatsToCoords():

    ###
    # Input: Acceleration Data, Quaternions, Velocity Data (Outputted from this script)
    # Output: Velocity Data, Position at last data point

    # -----------------1: IMPORT DATA---------------------------------------------------

    # aB = Linear Acceleration (Columns 4,5,6 in data.txt)
    # t = time (column 1 in data.txt)
    # Beta = quaternions (Columns 1,2,3,4)


    data = np.loadtxt("cleaned_data.txt", skiprows=1, dtype=float)  # Import data.txt file
    N = len(data)  # Find number of rows of data
    quats = np.loadtxt("quat.txt", dtype=float)
    # Beta = np.zeros((N, 4))  # Initialize quats (don't know how to get quat data from other function)
    # Beta = [Q[0], Q[1], Q[2], Q[3]] #Get quat data from other function

    t = data[:, 0] * 1e-6  # Time data (data.txt column 0)
    axB = data[:, 13] + x_a_offset# X coord Acc. data (data.txt column 3)
    ayB = data[:, 14] + y_a_offset
    azB = data[:, 15] + z_a_offset

    b0 = quats[:, 0]  # Quat 1 data (quat function column 3)
    b1 = quats[:, 1]
    b2 = quats[:, 2]
    b3 = quats[:, 3]

    barom = data[:, 8]
    start_altitude = barom[0]
    apogee_index = np.where(barom==min(barom))[0][0]
    max_barom_after_apogee = max(barom[apogee_index:])
    print('apogee index:',apogee_index)

    # -----------------2: Convert Quaternions into rotation matrix---------------------------

    RBIarray = []

    for i in range(len(quats)):
        RBIarray.append( [[(b0[i]**2)+(b1[i]**2)-(b2[i]**2)-(b3[i]**2),    2*((b1[i]*b2[i])+(b0[i]*b3[i])),       2*((b1[i]*b3[i])-(b0[i]*b2[i]))],
                       [2*((b1[i]*b2[i])-(b0[i]*b3[i])),        (b0[i]**2)-(b1[i]**2)+(b2[i]**2)-(b3[i]**2),      2*((b2[i]*b3[i])+(b0[i]*b1[i]))],
                       [2*((b1[i]*b3[i])+(b0[i]*b2[i])),            2*((b2[i]*b3[i])-(b0[i]*b1[i])),                (b0[i]**2)-(b1[i]**2)-(b2[i]**2)+(b3[i]**2)]] )

    RBIarray = np.array(RBIarray)
    # ----------------3: Convert Acc to Inertial Reference Frame----------------------------
    aB = []
    for i in range(len(quats)):
        aB.append([axB[i],ayB[i],azB[i]])
    aB = np.array(aB)
    aI = []  # Acc in Inertial Ref Frame (IRF)

    # Tried doing this for all data
    for i in range(len(quats)):
        aI.append( np.dot(np.linalg.inv(RBIarray[i]), np.transpose(aB[i]) )) # Acc in Inertial Ref Frame (IRF)
    aI = np.array(aI)

    for i in range(len(aI)):
        aI[i][2] -= 9.81


    # print(aI[1:10])

    # ----------------4: TrapZ integration of Inertial Acc to Inertial Vel----------------------

    vI = []
    
    # for j in range(len(quats)):
    #     temp_sumx = 0
    #     temp_sumy = 0
    #     temp_sumz = 0
    #     for k in range(1, j):
    #         temp_sumx += (t[k] - t[k-1]) * (aI[k][0] + aI[k-1][0]) * 0.5
    #         temp_sumy += (t[k] - t[k-1]) * (aI[k][1] + aI[k-1][1]) * 0.5
    #         temp_sumz += (t[k] - t[k-1]) * (aI[k][2] + aI[k-1][2]) * 0.5
    #     vI.append([temp_sumx, temp_sumy, temp_sumz])
    # vI = np.array(vI)

    vI = [[0,0,0]]

    

    for i in range(1,len(quats)):
        sumx = vI[i-1][0] + ((t[i] - t[i-1]) * (aI[i][0] + aI[i-1][0]) * 0.5)
        sumy = vI[i-1][1] + ((t[i] - t[i-1]) * (aI[i][1] + aI[i-1][1]) * 0.5)
        sumz = vI[i-1][2] + ((t[i] - t[i-1]) * (aI[i][2] + aI[i-1][2]) * 0.5)
        vI.append([sumx, sumy, sumz])
    vI = np.array(vI)

    # print(vI[1:10])

    print("final velocities:",vI[len(vI) - 1])

    # ----------------5: TrapZ integration of Inertial Vel to Inertial Pos----------------------
    
    dI = [[0,0,0]]
    sumx = sumy = sumz = 0
    z_max = z_max_line = 0
    j = 1
    # while j < (len(quats)-1) and not (j>apogee_index and barom[j] == max_barom_after_apogee):
    while j < (len(quats)-1) and not (j>apogee_index and barom[j] >= start_altitude):
    # while j < (len(quats)-1):
        sumx = dI[j-1][0] + ((t[j] - t[j-1]) * (vI[j][0] + vI[j-1][0]) * 0.5)
        sumy = dI[j-1][1] + ((t[j] - t[j-1]) * (vI[j][1] + vI[j-1][1]) * 0.5)
        sumz = dI[j-1][2] + ((t[j] - t[j-1]) * (vI[j][2] + vI[j-1][2]) * 0.5)

        dI.append([sumx, sumy, sumz])
        # sumx += (t[j] - t[j-1]) * (vI[j][0])
        # sumy += (t[j] - t[j-1]) * (vI[j][1])
        # sumz += (t[j] - t[j-1]) * (vI[j][2])

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

quatsToCoords()

   