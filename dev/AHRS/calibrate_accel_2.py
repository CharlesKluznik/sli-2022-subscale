import statistics


xsums = xraws = xoffsets = [0,0,0]
with open('x_accel_cal.txt','r') as file:
    file.readline()
    line = file.readline()
    lines_read = 0
    while line:
        data = line.split(' ')
        lines_read += 1
        xsums[0] += float(data[13])
        xsums[1] += float(data[14])
        xsums[2] += float(data[15])
        line = file.readline()

xraws[0] = xsums[0] / lines_read
xraws[1] = xsums[1] / lines_read
xraws[2] = xsums[2] / lines_read

ysums = yraws = yoffsets = [0,0,0]
with open('y_accel_cal.txt','r') as file:
    file.readline()
    line = file.readline()
    lines_read = 0
    while line:
        data = line.split(' ')
        lines_read += 1
        ysums[0] += float(data[13])
        ysums[1] += float(data[14])
        ysums[2] += float(data[15])
        line = file.readline()

yraws[0] = ysums[0] / lines_read
yraws[1] = ysums[1] / lines_read
yraws[2] = ysums[2] / lines_read


zsums = zraws = zoffsets = [0,0,0]
with open('z_accel_cal.txt','r') as file:
    file.readline()
    line = file.readline()
    lines_read = 0
    while line:
        data = line.split(' ')
        lines_read += 1
        zsums[0] += float(data[13])
        zsums[1] += float(data[14])
        zsums[2] += float(data[15])
        line = file.readline()

zraws[0] = zsums[0] / lines_read
zraws[1] = zsums[1] / lines_read
zraws[2] = zsums[2] / lines_read

print("X file raw:\t{0:+.9f}\t{1:+.9f}\t{2:+.9f}".format(xraws[0],xraws[1],xraws[2]))
print("Y file raw:\t{0:+.9f}\t{1:+.9f}\t{2:+.9f}".format(yraws[0],yraws[1],yraws[2]))
print("Z file raw:\t{0:+.9f}\t{1:+.9f}\t{2:+.9f}".format(zraws[0],zraws[1],zraws[2]))

xoffsets[0] = (abs(xraws[0])/xraws[0])*(9.81-abs(xraws[0]))
xoffsets[1] = -1*xraws[1]
xoffsets[2] = -1*xraws[2]

yoffsets[0] = -1*yraws[0]
yoffsets[1] = (abs(yraws[1])/yraws[1])*(9.81-abs(yraws[1]))
yoffsets[2] = -1*yraws[2]

zoffsets[0] = -1*zraws[0]
zoffsets[1] = -1*zraws[1]
zoffsets[2] = (abs(zraws[2])/zraws[2])*(9.81-abs(zraws[2]))

print("\nX averaged offset:\t{0:+.9f}".format(statistics.mean(xoffsets)))
print("Y averaged offset:\t{0:+.9f}".format(statistics.mean(yoffsets)))
print("Z averaged offset:\t{0:+.9f}".format(statistics.mean(zoffsets)))