from matplotlib import lines


x_sum = y_sum = z_sum = 0
with open('data_subscale_prelaunch.txt','r') as file:
    file.readline()
    line = file.readline()
    lines_read = 0
    while line:
        data = line.split(' ')
        lines_read += 1
        x_sum += float(data[10])
        y_sum += float(data[11])
        z_sum += float(data[12])
        line = file.readline()

x_raw = x_sum / lines_read
y_raw = y_sum / lines_read
z_raw = z_sum / lines_read

print("Raw X rotation: {0:+}".format(x_raw),", offset should be: {0:+}".format(-1*x_raw))
print("Raw Y rotation: {0:+}".format(y_raw),", offset should be: {0:+}".format(-1*y_raw))
print("Raw Z rotation: {0:+}".format(z_raw),", offset should be: {0:+}".format(-1*z_raw))