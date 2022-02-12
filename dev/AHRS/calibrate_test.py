import math

# Best offsets we have when tested on subscale prelaunch data <- found by calibrate_accel.py
x_a_offset = -0.01137564357366827
y_a_offset = 0.12418234651448756
z_a_offset = -0.04117713395608824

# Averaged offsets from the 3 different calibration tests <- found by calibrate_accel_2.py
# WORSE THAN THE ACCELERATION OFFSETS ABOVE
# x_a_offset = 0.068116729
# y_a_offset = -0.032484715
# z_a_offset = 0.026550351

x_r_offset = 0.03201130448281042
y_r_offset = -0.01767855554417916
z_r_offset = -0.00030196657169167786

# x_a_offset = y_a_offset = z_a_offset = x_r_offset = y_r_offset = z_r_offset = 0

mag_sum_a = mag_sum_r = 0
with open("data_subscale_prelaunch.txt",'r') as file:
    file.readline()
    line = file.readline()
    lines_read = 0
    while line:
        data = line.split(' ')
        x_r = float(data[10])
        y_r = float(data[11])
        z_r = float(data[12])
        x_a = float(data[13])
        y_a = float(data[14])
        z_a = float(data[15])
        mag_sum_a += math.sqrt((x_a + x_a_offset)**2 + (y_a + y_a_offset)**2 + (z_a + z_a_offset)**2)
        mag_sum_r += math.sqrt((x_r + x_r_offset)**2 + (y_r + y_r_offset)**2 + (z_r + z_r_offset)**2)
        lines_read += 1
        line = file.readline()


avg_mag_a = mag_sum_a / lines_read
avg_mag_r = mag_sum_r / lines_read

print("Avg Accel Mag:\t{0:+.9f}".format(avg_mag_a))
print("Offset by:\t{0:+.9f}".format(9.81-avg_mag_a))
print("Avg Rot Mag:\t{0:+.9f}".format(avg_mag_r))
print("Offset by:\t{0:+.9f}".format(-1*avg_mag_r))