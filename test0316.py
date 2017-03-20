# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 13:10:24 2017

@author: medialab
"""

import cPickle
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import gaussian_filter as gf



src_path = 'F:/Kinect Project/20170224/'

Kdata = cPickle.load(file(src_path+'Kinect data _ h5 and pkl file/shijie/shijie_data02241202_ex4.pkl','rb'))
Mdata = cPickle.load(file(src_path+'Shijie_Mcom_Ksyn.pkl','rb'))

Kx =[]
Ky =[]
Kz =[]

samplecnt = min(len(Kdata),Mdata[10].shape[1])

for i in xrange(samplecnt):

    Kx.append(Kdata[i]['joints'][10].Position.x)
    Ky.append(Kdata[i]['joints'][10].Position.y)
    Kz.append(Kdata[i]['joints'][10].Position.z)
    
Mx = Mdata[10][0,:][:samplecnt]
My = Mdata[10][1,:][:samplecnt]
Mz = Mdata[10][2,:][:samplecnt]

X = range(samplecnt)

plt.figure()

ax1 = plt.subplot(6,1,1)
ax1.set_title('Kinect_X')
plt.plot(X,Kx)
ax2 = plt.subplot(6,1,2)
ax2.set_title('Motion_X')
plt.plot(X,Mx)

ax3 = plt.subplot(6,1,3)
ax3.set_title('Kinect_Y')
plt.plot(X,Ky)
ax4 = plt.subplot(6,1,4)
ax4.set_title('Motion_Y')
plt.plot(X,My)

ax5 = plt.subplot(6,1,5)
ax5.set_title('Kinect_Z')
plt.plot(X,Kz)
ax6 = plt.subplot(6,1,6)
ax6.set_title('Motion_Z')
plt.plot(X,Mz)

plt.show()



NKx = (np.array(Kx)-np.mean(Kx))/np.std(Kx)
NKy = (np.array(Ky)-np.mean(Ky))/np.std(Ky)
NKz = (np.array(Kz)-np.mean(Kz))/np.std(Kz)

NMx = (Mx-np.mean(Mx))/np.std(Mx)
NMy = (My-np.mean(My))/np.std(My)
NMz = (Mz-np.mean(Mz))/np.std(Mz)


#plt.figure()
#
#ax1 = plt.subplot(6,1,1)
#ax1.set_title('Kinect_X')
#plt.plot(X,NKx)
#ax2 = plt.subplot(6,1,2)
#ax2.set_title('Motion_X')
#plt.plot(X,NMx)
#
#ax3 = plt.subplot(6,1,3)
#ax3.set_title('Kinect_Y')
#plt.plot(X,NKy)
#ax4 = plt.subplot(6,1,4)
#ax4.set_title('Motion_Y')
#plt.plot(X,NMy)
#
#ax5 = plt.subplot(6,1,5)
#ax5.set_title('Kinect_Z')
#plt.plot(X,NKz)
#ax6 = plt.subplot(6,1,6)
#ax6.set_title('Motion_Z')
#plt.plot(X,NMz)
#
#plt.show()



plt.figure()

ax1 = plt.subplot(6,1,1)
ax1.set_title('Kinect_X')
plt.plot(X,gf(Kx,3))
ax2 = plt.subplot(6,1,2)
ax2.set_title('Motion_X')
plt.plot(X,Mx)

ax3 = plt.subplot(6,1,3)
ax3.set_title('Kinect_Y')
plt.plot(X,gf(Ky,3))
ax4 = plt.subplot(6,1,4)
ax4.set_title('Motion_Y')
plt.plot(X,My)

ax5 = plt.subplot(6,1,5)
ax5.set_title('Kinect_Z')
plt.plot(X,gf(Kz,3))
ax6 = plt.subplot(6,1,6)
ax6.set_title('Motion_Z')
plt.plot(X,Mz)



plt.show()




