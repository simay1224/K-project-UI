# import numpy as np
# from sklearn.gaussian_process import GaussianProcessRegressor
# from sklearn.gaussian_process.kernels import RBF, WhiteKernel,ConstantKernel
# from sklearn.externals import joblib
# import _pickle as cPickle
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# ############# read kernel file##############


# M_data = cPickle.load(open('tracking_data.pkl','rb'))

# K_EL = M_data['K_WL']
# M_EL = M_data['M_WL']
# K2M_spread_EL = M_data['K2M_spread_WL']
# K2M_spread_EL = M_data['K2M_spread_WL']


fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot(K2M_EL[:,0], K2M_EL[:,1], K2M_EL[:,2], label='proposed method using clustered training data',linewidth=2,color='red')
ax.plot(M_EL[:,0], M_EL[:,1], M_EL[:,2], label='MOCAP data',linewidth=2,color='orange')
ax.plot(K_EL[:,0], K_EL[:,1], K_EL[:,2], label='kinect data',linewidth=2,color='blue')
ax.plot(K2M_spread_EL[:,0], K2M_spread_EL[:,1], K2M_spread_EL[:,2],label='[6]',linewidth=2,color='green')

idx = [199, 188, 190 , 183]
idx2 = [199, 188, 190 , 182]
m    = ["o", ">", "s" , "p"]
size = 250

for i in range(4):
    ax.scatter(K2M_EL[idx2[i],0], K2M_EL[idx2[i],1], K2M_EL[idx2[i],2], s = size, color='red',marker=m[i])
    # ax.scatter(K2M_EL[idx2,0], K2M_EL[idx2,1], K2M_EL[idx2,2], s = size, color='red',marker=">")
    ax.scatter(M_EL[idx[i],0], M_EL[idx[i],1], M_EL[idx[i],2], s = size, color='orange',marker=m[i])
    ax.scatter(K_EL[idx[i],0], K_EL[idx[i],1], K_EL[idx[i],2], s = size ,color='blue',marker=m[i])
    ax.scatter(K2M_spread_EL[idx[i],0], K2M_spread_EL[idx[i],1], K2M_spread_EL[idx[i],2], s = size ,color='green',marker=m[i])






ax.set_xlabel('Z axis')
ax.set_ylabel('X axis')
ax.set_zlabel('Y axis')

ax.legend()
plt.show()



