'''
Q4.2:
    1. Integrating everything together.
    2. Loads necessary files from ../data/ and visualizes 3D reconstruction using scatter
'''

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import submission
import helper

pts = np.load('../data/some_corresp.npz')
pts1 = pts['pts1']
pts2 = pts['pts2']

K = np.load('../data/intrinsics.npz')
K1 = K['K1']
K2 = K['K2']

temple_xy = np.load('../data/templeCoords.npz')
x1 = temple_xy['x1']
y1 = temple_xy['y1']
temple_pts1 = np.hstack((x1,y1))
im1 = plt.imread('../data/im1.png')
im2 = plt.imread('../data/im2.png')
M = np.max(im1.shape)

F = submission.eightpoint(pts1, pts2, M) # EightPoint algrithm to find F
E = submission.essentialMatrix(F, K1, K2)
x2 = np.empty((x1.shape[0],1))
y2 = np.empty((x1.shape[0],1))
for i in range(x1.shape[0]):
    corresp = submission.epipolarCorrespondence(im1, im2, F, x1[i], y1[i])
    x2[i] = corresp[0]
    y2[i] = corresp[1]

temple_pts2 = np.hstack((x2,y2))

M1 = np.eye(3)
M1 = np.hstack((M1, np.zeros([3,1])))
M2_all = helper.camera2(E)

C1 = np.dot(K1 , M1)
err_val = np.inf

for i in range(M2_all.shape[2]):
    C2 = np.dot(K2 , M2_all[:,:,i])
    w,err = submission.triangulate(C1, temple_pts1 , C2, temple_pts2)

    if (err < err_val and np.min(w[:,2]) >= 0):

        err_val = err
        M2 = M2_all[:,:,i]
        C2_best = C2
        C2 = C2_best
        w_best = w

np.savez('q4_2.npz', F = F, M1 = M1, M2 = M2, C1 = C1, C2 = C2)
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
ax.set_xlim3d(np.min(w_best[:,0]),np.max(w_best[:,0]))
ax.set_ylim3d(np.min(w_best[:,1]),np.max(w_best[:,1]))
ax.set_zlim3d(np.min(w_best[:,2]),np.max(w_best[:,2]))
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.scatter(w_best[:,0],w_best[:,1],w_best[:,2])
plt.show()
