x_sum = y_sum = z_sum = 0
with open('x_accel_cal.txt','r') as file:
    file.readline()
    line = file.readline()
    x_lines_read = 0
    while line:
        data = line.split(' ')
        x_lines_read += 1
        x_sum += float(data[13])
        line = file.readline()


with open('y_accel_cal.txt','r') as file:
    file.readline()
    line = file.readline()
    y_lines_read = 0
    while line:
        data = line.split(' ')
        y_lines_read += 1
        y_sum += float(data[14])
        line = file.readline()

        

with open('z_accel_cal.txt','r') as file:
    file.readline()
    line = file.readline()
    z_lines_read = 0
    while line:
        data = line.split(' ')
        z_lines_read += 1
        z_sum += float(data[15])
        line = file.readline()


x_raw = x_sum / x_lines_read
y_raw = y_sum / y_lines_read
z_raw = z_sum / z_lines_read

print("x_raw = ",x_raw, "\toffset should be {0:+}".format((abs(x_raw)/x_raw)*(9.81-abs(x_raw))))
print("y_raw = ",y_raw, "\toffset should be {0:+}".format((abs(y_raw)/y_raw)*(9.81-abs(y_raw))))
print("z_raw = ",z_raw, "\toffset should be {0:+}".format((abs(z_raw)/z_raw)*(9.81-abs(z_raw))))



