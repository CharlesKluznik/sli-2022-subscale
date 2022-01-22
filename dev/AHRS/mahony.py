from math import sqrt

class AHRS():
    # System constants
    gyroMeasError = 3.14159265358979 * (5.0 / 180.0) # gyroscope measurement error in rad/s (shown as 5 deg/s)
    beta  = sqrt(3.0 / 4.0) * gyroMeasError # compute beta
    # Global system variables
    # accelerometer measurements
    a_x: float
    a_y: float
    a_z: float 
    # gyroscope measurements in rad/s
    w_x: float
    w_y: float
    w_z: float 
    # estimated orientation quaternion elements with initial conditions
    SEq_1: float = 1.0
    SEq_2: float = 0.0
    SEq_3: float = 0.0
    SEq_4: float = 0.0

    #deltat is sampling period in SECONDS
    def filter_update(self, w_x: float, w_y: float, w_z: float, a_x: float, a_y: float, a_z: float, deltat: float):
        # Local system variables
        norm: float # vector norm
        # quaternion derivative from gyroscopes elements 
        SEqDot_omega_1: float
        SEqDot_omega_2: float
        SEqDot_omega_3: float
        SEqDot_omega_4: float 
        # objective function elements
        f_1: float
        f_2: float
        f_3: float
        # objective function Jacobian elements
        J_11or24: float
        J_12or23: float 
        J_13or22: float
        J_14or21: float
        J_32: float
        J_33: float
        # estimated direction of the gyroscope error
        SEqHatDot_1: float
        SEqHatDot_2: float
        SEqHatDot_3: float
        SEqHatDot_4: float
        # Auxilary variables to avoid reapeated calcualtions
        halfSEq_1: float = 0.5 * self.SEq_1
        halfSEq_2: float = 0.5 * self.SEq_2
        halfSEq_3: float = 0.5 * self.SEq_3
        halfSEq_4: float = 0.5 * self.SEq_4
        twoSEq_1: float = 2.0 * self.SEq_1
        twoSEq_2: float = 2.0 * self.SEq_2
        twoSEq_3: float = 2.0 * self.SEq_3
        # Normalise the accelerometer measurement
        norm = sqrt(a_x * a_x + a_y * a_y + a_z * a_z)
        a_x /= norm
        a_y /= norm
        a_z /= norm
        # Compute the objective function and Jacobian
        f_1 = twoSEq_2 * self.SEq_4 - twoSEq_1 * self.SEq_3 - a_x
        f_2 = twoSEq_1 * self.SEq_2 + twoSEq_3 * self.SEq_4 - a_y
        f_3 = 1.0 - twoSEq_2 * self.SEq_2 - twoSEq_3 * self.SEq_3 - a_z
        J_11or24 = twoSEq_3 # J_11 negated in matrix multiplication
        J_12or23 = 2.0 * self.SEq_4
        J_13or22 = twoSEq_1 # J_12 negated in matrix multiplication
        J_14or21 = twoSEq_2
        J_32 = 2.0 * J_14or21 # negated in matrix multiplication
        J_33 = 2.0 * J_11or24 # negated in matrix multiplication
        # Compute the gradient (matrix multiplication)
        SEqHatDot_1 = J_14or21 * f_2 - J_11or24 * f_1
        SEqHatDot_2 = J_12or23 * f_1 + J_13or22 * f_2 - J_32 * f_3
        SEqHatDot_3 = J_12or23 * f_2 - J_33 * f_3 - J_13or22 * f_1
        SEqHatDot_4 = J_14or21 * f_1 + J_11or24 * f_2
        # Normalise the gradient
        norm = sqrt(SEqHatDot_1 * SEqHatDot_1 + SEqHatDot_2 * SEqHatDot_2 + SEqHatDot_3 * SEqHatDot_3 + SEqHatDot_4 * SEqHatDot_4)
        SEqHatDot_1 /= norm
        SEqHatDot_2 /= norm
        SEqHatDot_3 /= norm
        SEqHatDot_4 /= norm
        # Compute the quaternion derrivative measured by gyroscopes
        SEqDot_omega_1 = -halfSEq_2 * w_x - halfSEq_3 * w_y - halfSEq_4 * w_z
        SEqDot_omega_2 = halfSEq_1 * w_x + halfSEq_3 * w_z - halfSEq_4 * w_y
        SEqDot_omega_3 = halfSEq_1 * w_y - halfSEq_2 * w_z + halfSEq_4 * w_x
        SEqDot_omega_4 = halfSEq_1 * w_z + halfSEq_2 * w_y - halfSEq_3 * w_x
        # Compute then integrate the estimated quaternion derrivative
        self.SEq_1 += (SEqDot_omega_1 - (self.beta * SEqHatDot_1)) * deltat
        self.SEq_2 += (SEqDot_omega_2 - (self.beta * SEqHatDot_2)) * deltat
        self.SEq_3 += (SEqDot_omega_3 - (self.beta * SEqHatDot_3)) * deltat
        self.SEq_4 += (SEqDot_omega_4 - (self.beta * SEqHatDot_4)) * deltat
        # Normalise quaternion
        norm = sqrt(self.SEq_1 * self.SEq_1 + self.SEq_2 * self.SEq_2 + self.SEq_3 * self.SEq_3 + self.SEq_4 * self.SEq_4)
        self.SEq_1 /= norm
        self.SEq_2 /= norm
        self.SEq_3 /= norm
        self.SEq_4 /= norm