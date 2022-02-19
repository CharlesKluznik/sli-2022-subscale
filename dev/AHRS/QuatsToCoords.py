import numpy as np
'''
Input: Acceleration Data, Quaternions, Velocity Data (Outputted from this script)
Output: Velocity Data, Position at last data point
'''
# -----------------1: IMPORT DATA---------------------------------------------------
'''
aB = Linear Acceleration (Columns 4,5,6 in data.txt)
t = time (column 1 in data.txt)
Beta = quaternions (Columns 1,2,3,4)
'''

data = np.loadtxt("data.txt", skiprows=1, dtype=float)  # Import data.txt file
N = len(data)  # Find number of rows of data
Beta = np.zeros((N, 4))  # Initialize quats (don't know how to get quat data from other function)
# Beta = [Q[0], Q[1], Q[2], Q[3]] #Get quat data from other function

t = data[:, 0]  # Time data (data.txt column 0)
axB = data[:, 3]  # X coord Acc. data (data.txt column 3)
ayB = data[:, 4]
azB = data[:, 5]

b0 = Beta[:, 0]  # Quat 1 data (quat function column 3)
b1 = Beta[:, 1]
b2 = Beta[:, 2]
b3 = Beta[:, 3]

# -----------------2: Convert Quaternions into rotation matrix---------------------------
# From Aero 3520 Matlab script
RBI = [[b0**2+b1**2-b2**2-b3**2,       2*(b1*b2+b0*b3),       2*(b1*b3-b0*b2)],
       [2*(b1*b2-b0*b3),   b0**2-b1**2+b2**2-b3**2,       2*(b2*b3+b0*b1)],
       [2*(b1*b3+b0*b2),       2*(b2*b3-b0*b1),   b0**2-b1**2-b2**2+b3**2]]

''' Tried doing this for all data
for i in Beta:
    RBIarray = [[b0[i]**2+b1[i]**2-b2[i]**2-b3[i]**2,       2*(b1[i]*b2[i]+b0[i]*b3[i]),       2*(b1[i]*b3[i]-b0[i]*b2[i])],
                [2*(b1[i]*b2[i]-b0[i]*b3[i]),   b0[i]**2-b1[i]**2+b2[i]**2-b3[i]**2,       2*(b2[i]*b3[i]+b0[i]*b1[i])],
                [2*(b1[i]*b3[i]+b0[i]*b2[i]),       2*(b2[i]*b3[i]-b0[i]*b1[i]),   b0[i]**2-b1[i]**2-b2[i]**2+b3[i]**2]]
'''
# ----------------3: Convert Acc to Inertial Reference Frame----------------------------
aB = np.transpose([axB, ayB, azB])  # Acc in Body Ref Frame (BRF)
aI = np.zeros((N, 3))  # Acc in Inertial Ref Frame (IRF)

'''Tried doing this for all data
for i in range(1, N):
    aI[i] = RBI * aB[i]  # Acc in Inertial Ref Frame (IRF)
'''

# ----------------4: TrapZ integration of Inertial Acc to Inertial Vel----------------------
# Find sum of acceleration data
aB_sum = ab[0]
vB_sum = vb[0]

# find summation for acceleration data
for i in aB:
    if i == N:
        aB_sum = aB_sum + ab[i]
    else:
        aB_sum = aB_sum + 2*ab[i]

# find velocity at last point in data
dx = t[N] - t[N-1]
vI = (dx/2) * ab_sum

# ----------------5: TrapZ integration of Inertial Vel to Inertial Pos----------------------

# find summation for acceleration data
for i in vB:
    if i == N:
        vB_sum = vB_sum + vb[i]
    else:
        vB_sum = vB_sum + 2*vb[i]

# find position at last point in data
dx = t[N] - t[N-1]
rI = (dx/2) * vb_sum
