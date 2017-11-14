import os, glob, pdb
import h5py, cPickle
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter1d as gf
import matplotlib.pyplot as plt

src_path = './output/'
cnt = 1
def getcoord(data, order=[1, 4, 8, 20]):   
    for i in order:
        if i == 1:
            tmp = np.array([data[i].x, data[i].y])
        else:
            tmp = np.vstack([tmp, np.array([data[i].x, data[i].y])])
    return tmp



for dfile, infile in zip(glob.glob(os.path.join(src_path, '*.h5')),\
                         glob.glob(os.path.join(src_path, '*.pkl'))):
    print dfile
    print infile
    d_data = h5py.File(dfile,'r')['imgs']['dimgs']
    data   = cPickle.load(file(infile, 'rb'))
    result = []
    for idx,key in enumerate(d_data.keys()):
        dimg = d_data[key][:][:, :, 0]
        coord = getcoord(data[idx]['depth_jointspts'])
        ub = int(coord[0][1])-10  # upper bound
        bb = int(coord[3][1])     # lower bound
        lb = int(coord[1][0])+10  # left bound
        rb = int(coord[2][0])-10  # right bound
        mask = np.zeros((424, 512))
        mask[bb:ub, lb:rb] = 1
        # print ub-bb
        # print rb-lb
        if idx == 0:
            ref_mask = mask == 1
            ref_dimg = dimg
        else:
            cur_mask = ref_mask & (mask==1)
            # print np.sum(cur_mask)
            ref_dblk = ndimage.gaussian_filter(ref_dimg*cur_mask, sigma=(2, 2), order=0).astype(float)
            cur_dblk = ndimage.gaussian_filter(dimg*cur_mask, sigma=(2, 2), order=0).astype(float)
            blk_mad = np.mean(np.abs(ref_dblk[cur_mask]-cur_dblk[cur_mask]))
            result.append(blk_mad)
    plt.figure(cnt)        
    plt.plot(gf(result,3))
    cnt += 1
plt.show()    
