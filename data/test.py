import cPickle
import numpy as np
import glob, os
from math import acos
import matplotlib.pyplot as plt

def el_angle(data, idx=[4, 5, 6]):
    vec1 = np.array([data[idx[0]].x-data[idx[1]].x, data[idx[0]].y-data[idx[1]].y])
    vec2 = np.array([data[idx[2]].x-data[idx[1]].x, data[idx[2]].y-data[idx[1]].y])
    costheta = vec1.dot(vec2)/sum(vec1**2)**.5/sum(vec2**2)**.5
    return acos(costheta)*180/np.pi

angle = []
th = 140
per = 10
stus = []

for infile in glob.glob(os.path.join('', '*.pkl'))[:1]:
    data = cPickle.load(file(infile, 'rb'))
    for fnum in xrange(len(data)):
        joints = data[fnum]['jointspts']
        angle.append(el_angle(joints))
        if angle < per:
            mean_angle = np.mean(angle)
        else:
            mean_angle = np.mean(angle[-per:])
        if mean_angle >= th:
            stus.append(100)
        else:
            stus.append(50)

plt.plot(angle)
plt.plot(stus)
plt.show()

