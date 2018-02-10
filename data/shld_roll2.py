import numpy as np
import cPickle 
import glob, os
from scipy.ndimage.filters import gaussian_filter1d as gf
import h5py
import matplotlib.pyplot as plt
import cv2
import pdb
from scipy.signal import argrelextrema

def findtops(bdimg, shld, bdidx):
    return np.where(bdimg[:shld[1], shld[0]] != bdidx)[0][::-1][0]+1


def findminmax(data, rng=50, start=0, ignore=10, dtype='height'):
    foo = argrelextrema(gf(data, 5), np.less_equal, order=rng)[0]
    vall = foo[np.where((np.roll(foo, 1)-foo) != -1)[0]]
    vall = vall[vall >= ignore][start:]
    foo = argrelextrema(gf(data, 5), np.greater_equal, order=rng)[0]
    peak = foo[np.where((np.roll(foo, 1)-foo) != -1)[0]]
    peak = peak[peak >= ignore][start:]
    if dtype == 'height':
        return [peak, vall]
    elif dtype == 'depth':
        peakvalue = gf(data, 5)[peak]
        vallvalue = gf(data, 5)[vall]
        return [peak, vall, peakvalue, vallvalue]

def chkdepth(peak, vall, th=30):
    if len(peak) == len(vall):
        if (peak[-1]-vall[-1]) > th:
            return True
        else:
            return False
    else:
        if len(peak) > len(vall):
            if (peak[-2]-vall[-1]) > th:
                return True
            else:
                return False 
        else:
            if (peak[-1]-vall[-2]) > th:
                return True
            else:
                return False             


def findcycle(y, z, trig=0):
    
    # if len(y[0]) == 0 or len(y[1]) == 0 or len(z[0]) == 0 or len(z[1]) == 0:
    #     return 0, trig
    if (max(len(y[0]), len(y[1]), len(z[0]), len(z[1])) \
        - min(len(y[0]), len(y[1]), len(z[0]), len(z[1]))) > 1:
        return 0 #, trig

    # num1 = (len(y[0])+len(y[1])+len(z[0])+len(z[1]))%4
    num2 = (len(y[0])+len(y[1])+len(z[0])+len(z[1])-1)/4

    if num2 > 0:
        chk = chkdepth(z[2], z[3])
        if chk:
            return 1
        else:
            return 2
    else:
        return 0


Lylist = []
Ldlist = []
yplist = []
yvlist = []
zplist = []
zvlist = []




cycle = False
cnt   = 0
ign   = 30
flag  = True
# trig  = 4
rng   = 50


src_path = './output/'

for pkl_file, h5_file in zip(glob.glob(os.path.join(src_path, '*.pkl'))\
                           , glob.glob(os.path.join(src_path, '*.h5')))[4:5]:

    data = cPickle.load(file(pkl_file,'rb'))      
    f = h5py.File(h5_file,'r')

    for fnum in xrange(len(data)): # xrange(65, 160): #

        bdimg = f['imgs']['bdimgs']['bd_'+'{0:04}'.format(fnum)][:, :, 0]
        depth = f['imgs']['dimgs']['d_'+'{0:04}'.format(fnum)][:, :, 0]
        joints = data[fnum]['depth_jointspts']

        lshld = [int(joints[4].x), int(joints[4].y)]
        rshld = [int(joints[4].x), int(joints[4].y)]

        Lylist.append(lshld[1])
        Ldlist.append(depth[lshld[1], lshld[0]])

        if (fnum >= 50) and (fnum%20 == 0):
            newcnt = 0
            
            ylist = findminmax(Lylist, rng, cnt, ignore=ign, dtype='height')
            zlist = findminmax(Ldlist, rng, cnt, ignore=ign, dtype='depth')
            # if len(ylist[0]) != 0 and flag:
            #     flag = False
            #     ign = ylist[0][0]
            if len(ylist[0]) and len(ylist[1]) and len(zlist[0]) and len(zlist[1]) and flag:
                flag = False
                ign = min(ylist[0][0], ylist[1][0], zlist[0][0], zlist[1][0])


            print 'yvall : ' + str(ylist[1])
            print 'ypeak : ' + str(ylist[0])
            print 'zvall : ' + str(zlist[1])
            print 'zpeak : ' + str(zlist[0])
            print '\n'
            # pdb.set_trace()
            newcnt = findcycle(ylist, zlist)#, trig)

            if newcnt == 1:
                cnt += newcnt
                print 'cycle counts : ' + str(cnt)
                yplist.append(ylist[0][0])
                yvlist.append(ylist[1][0])
                zplist.append(zlist[0][0])
                zvlist.append(zlist[1][0])
            elif newcnt == 2:
                print 'it is just simple up and down'

        cv2.imshow('frame', bdimg)
        cv2.waitKey(30) & 0xff
    f.close()

plt.ion()
plt.figure(2)
plt.subplot(2, 1, 1)
plt.plot(gf(Lylist, 5))
plt.scatter(yvlist, gf(Lylist,5)[np.array(yvlist)], c='r')
plt.scatter(yplist, gf(Lylist,5)[np.array(yplist)], c='g')
plt.subplot(2, 1, 2)
plt.plot(gf(Ldlist, 5))
plt.scatter(zvlist, gf(Ldlist,5)[np.array(zvlist)], c='r')
plt.scatter(zplist, gf(Ldlist,5)[np.array(zplist)], c='g')
plt.show()

# plt.figure(1)
# plt.subplot(2, 1, 1)
# plt.plot(gf(Lylist, 5))
# plt.scatter(ylist[1], gf(Lylist,5)[ylist[1]], c='r')
# plt.scatter(ylist[0], gf(Lylist,5)[ylist[0]], c='g')
# plt.subplot(2, 1, 2)
# plt.plot(gf(Ldlist, 5))
# plt.scatter(zlist[1], gf(Ldlist,5)[zlist[1]], c='r')
# plt.scatter(zlist[0], gf(Ldlist,5)[zlist[0]], c='g')
# plt.show()