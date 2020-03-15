'''
Q4.2:
    1. Integrating everything together.
    2. Loads necessary files from ../data/ and visualizes 3D reconstruction using scatter
'''
import matplotlib.pyplot as plt
import numpy as np
import submission
import helper

pts = np.load('../data/some_corresp.npz')
pts1 = pts['pts1']
pts2 = pts['pts2']

K = np.load('../data/intrinsics.npz')
K1 = K['K1']
K2 = K['K2']

coord = np.load('../data/templeCoords.npz')
x1 = coord['x1']
y1 = coord['y1']

im1 = plt.imread('../data/im1.png')
im2 = plt.imread('../data/im2.png')
M = np.max(im1.shape)

F = submission.eightpoint(pts1, pts2, M) # EightPoint algrithm to find F
E = submission.essentialMatrix(F, K1, K2)
x2 = []
y2 = []
for i in range(pts1.shape[0]):
    corresp = submission.epipolarCorrespondence(im1, im2, F, x1[i][0], y1[i][0])
    x2.append(corresp[0])
    y2.append(corresp[1])

x2 = np.asarray(x2)
y2 = np.asarray(y2)

M1 = np.eye(3)
M1 = np.hstack((M1, np.zeros([3,1])))
M2_all = helper.camera2(E)

C1 = np.dot(K1 , M1)
err_val = np.inf

for i in range(M2_all.shape[2]):

    C2 = np.dot(K2 , M2_all[:,:,i])
    w,err = submission.triangulate(C1, pts1, C2, pts2)

    if err < err_val:
        err_val = err
        M2 = M2_all[:,:,i]
        C2_best = C2
        w_best = w

fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
ax.scatter(w_best[:,0],w_best[:,1],w_best[:,2])
plt.show()