import numpy as np

SECS_BEFORE_APOGEE = 30
SECS_AFTER_APOGEE = 100


data = np.loadtxt("data_subscale.txt", skiprows=1, dtype=float)
barom = data[:, 8]
apogee_index = np.where(barom==min(barom))[0][0]
lines_written = 0
with open("data_subscale.txt", "r") as inFile:
    line = inFile.readline()
    with open("cleaned_data.txt", "w") as outFile:
        while line:
            line = inFile.readline()
            if len(line) > 0:
                tokens = line.split(' ')
                if (data[apogee_index][0] - (SECS_BEFORE_APOGEE * 1e6) < float(tokens[0]) and float(tokens[0]) < data[apogee_index][0] + (SECS_AFTER_APOGEE * 1e6)):
                    outFile.write(line)
                    lines_written+=1
                    # print(lines_written)