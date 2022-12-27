from matplotlib import pyplot as plt
from statistics import mean, median
from collections import OrderedDict
from os import path


basePath = path.dirname(path.realpath(__file__))
with open(path.join(basePath, "time_balanced.csv")) as f:
    lines = f.readlines()

data = []
for l in lines:
    l = l.split(",")
    head = l[0].strip()
    head = head.replace("True", "T")
    head = head.replace("False", "F")
    time = [float(t.strip()) for t in l[1:]]
    data.append((head, time))

labels, time = zip(*sorted(data, key=lambda x: mean(x[1])))
plt.boxplot(time, labels=labels)
plt.semilogy()
plt.xticks(rotation=90)
plt.show()
