import math

x_offset = -0.01137564357366827
y_offset = 0.12418234651448756
z_offset = -0.04117713395608824

mag_sum = 0
with open("data_subscale_prelaunch.txt",'r') as file:
    file.readline()
    line = file.readline()
    lines_read = 0
    while line:
        data = line.split(' ')
        x = float(data[13])
        y = float(data[14])
        z = float(data[15])
        mag_sum += math.sqrt((x + x_offset)**2 + (y + y_offset)**2 + (z + z_offset)**2)

        lines_read += 1
        line = file.readline()


avg_mag = mag_sum / lines_read

print("Average Magnitude: ", avg_mag)
print("Offset by {0:+}".format(9.81-avg_mag))