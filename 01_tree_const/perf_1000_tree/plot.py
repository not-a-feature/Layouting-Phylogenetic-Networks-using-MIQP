from matplotlib import pyplot as plt
from statistics import mean
from collections import OrderedDict
from os import path
from math import floor

basePath = path.dirname(path.realpath(__file__))


def readFiles(fn):
    with open(path.join(basePath, fn)) as f:
        lines = f.readlines()

    data = []
    for l in lines:
        l = l.split(",")
        head = l[0].strip()
        time = [float(t.strip()) for t in l[1:]]
        data.append((head, time))

    labels, time = zip(*data)
    labels = [l + "" for l in labels]
    return labels, time


def box_plot(data, labels, edge_color, fill_color, pos):
    bp = ax.boxplot(data, labels=labels, patch_artist=True, positions=pos)

    plt.setp(bp["medians"], color="black")

    for patch in bp["boxes"]:
        patch.set(facecolor=fill_color)

    return bp


labelsU, timeU = readFiles("unbalanced.csv")[:36]
labelsB, timeB = readFiles("balanced.csv")[:36]

posU = list(range(3, len(labelsU) * 2 + 2, 2))
posB = list(range(4, len(labelsB) * 2 + 3, 2))

fig, ax = plt.subplots(figsize=(10, 4))
bp1 = box_plot(timeU, None, "black", "#3D588C", pos=posU)
bp2 = box_plot(timeB, None, "black", "#D22B34", pos=posB)
ax.legend([bp1["boxes"][0], bp2["boxes"][0]], ["Unbalanced", "Balanced"])
ticks = [i + 0.5 for i in range(3, 83, 2)]
ax.set(xticks=ticks, xticklabels=list(range(3, 43)))
plt.semilogy()
plt.show()
