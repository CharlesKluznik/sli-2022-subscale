import numpy as np
import pandas as pd

x_a_offset = -0.01137564357366827
y_a_offset = 0.12418234651448756
z_a_offset = -0.04117713395608824

def quatsToCoords():

    ###
    # Input: Acceleration Data, Quaternions, Velocity Data (Outputted from this script)
    # Output: Velocity Data, Position at last data point

    # -----------------1: IMPORT DATA---------------------------------------------------

    # aB = Linear Acceleration (Columns 4,5,6 in data.txt)
    # t = time (column 1 in data.txt)
    # Beta = quaternions (Columns 1,2,3,4)


    data = np.loadtxt("data_accel_cal.txt", skiprows=1, dtype=float)  # Import data.txt file
    N = len(data)  # Find number of rows of data
    quats = np.loadtxt("quat.txt", dtype=float)
    # Beta = np.zeros((N, 4))  # Initialize quats (don't know how to get quat data from other function)
    # Beta = [Q[0], Q[1], Q[2], Q[3]] #Get quat data from other function

    t = data[:, 0]  # Time data (data.txt column 0)
    axB = data[:, 4] # X coord Acc. data (data.txt column 3)
    ayB = data[:, 5] 
    azB = data[:, 6] 

    b0 = quats[:, 0]  # Quat 1 data (quat function column 3)
    b1 = quats[:, 1]
    b2 = quats[:, 2]
    b3 = quats[:, 3]

    # -----------------2: Convert Quaternions into rotation matrix---------------------------
    # From Aero 3520 Matlab script
    # RBI = [[b0**2+b1**2-b2**2-b3**2,       2*(b1*b2+b0*b3),       2*(b1*b3-b0*b2)],
    #     [2*(b1*b2-b0*b3),   b0**2-b1**2+b2**2-b3**2,       2*(b2*b3+b0*b1)],
    #     [2*(b1*b3+b0*b2),       2*(b2*b3-b0*b1),   b0**2-b1**2-b2**2+b3**2]]
    

    RBIarray = []

    for i in range(len(quats)):
        RBIarray.append( [[b0[i]**2+b1[i]**2-b2[i]**2-b3[i]**2,    2*(b1[i]*b2[i]+b0[i]*b3[i]),                2*(b1[i]*b3[i]-b0[i]*b2[i])],
                       [2*(b1[i]*b2[i]-b0[i]*b3[i]),            b0[i]**2-b1[i]**2+b2[i] ** 2-b3[i]**2,      2*(b2[i]*b3[i]+b0[i]*b1[i])],
                       [2*(b1[i]*b3[i]+b0[i]*b2[i]),            2*(b2[i]*b3[i]-b0[i]*b1[i]),                b0[i]**2-b1[i]**2-b2[i]**2+b3[i]**2]] )

    RBIarray = np.array(RBIarray)
    # ----------------3: Convert Acc to Inertial Reference Frame----------------------------
    # aB = np.transpose([axB, ayB, azB])  # Acc in Body Ref Frame (BRF)
    aB = []
    for i in range(len(data)):
        aB.append([axB[i],ayB[i],azB[i]])
    aB = np.array(aB)
    aI = []  # Acc in Inertial Ref Frame (IRF)

    # Tried doing this for all data
    for i in range(len(quats)):
        aI.append( np.dot(np.linalg.inv(RBIarray[i]), np.transpose(aB[i]) )) # Acc in Inertial Ref Frame (IRF)
    aI = np.array(aI)

    # ----------------4: TrapZ integration of Inertial Acc to Inertial Vel----------------------

    # vI = []
    
    # for j in range(len(quats)):
    #     temp_sum = aI[0]
    #     for k in range(1, j):
    #         temp_sum += (2 * aI[k])
    #     temp_sum += aI[j]
    #     vI.append( (t[j] - t[0]) * temp_sum * 0.5 * 1e-6)
    # vI = np.array(vI)
    
    vI = []
    
    for j in range(len(quats)):
        temp_sum = aI[0]
        for k in range(1, j):
            temp_sum += (2 * aI[k])
        temp_sum += aI[j]
        vI.append( (t[j] - t[0]) * temp_sum * 0.5 * 1e-6)
    vI = np.array(vI)

    # ----------------5: TrapZ integration of Inertial Vel to Inertial Pos----------------------

    # dI = []
    # temp_sum = vI[0]
    # for j in range(len(quats)):
    #     temp_sum = aI[0]
    #     for k in range(1, j):
    #         temp_sum += (2 * vI[k])
    #     temp_sum += vI[j]
    #     dI.append( (t[j] - t[0]) * temp_sum * 0.5 * 1e-6)

    dI = []
    temp_sum = vI[0]
    for j in range(len(quats)):
        temp_sum += (2 * vI[k])
        temp_sum += vI[j]
        dI.append( (t[j] - t[0]) * temp_sum * 0.5 * 1e-6)

    dI = np.array(dI)

    print(dI[len(dI) -1])



quatsToCoords()

