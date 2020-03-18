"""Homework4.
Replace 'pass' by your implementation.
"""

# Insert your package here
import numpy as np
import helper
import pdb
import math
import matplotlib.pyplot as plt
'''
Q2.1: Eight Point Algorithm
    Input:  pts1, Nx2 Matrix
            pts2, Nx2 Matrix
            M, a scalar parameter computed as max (imwidth, imheight)
    Output: F, the fundamental matrix
'''
def eightpoint(pts1, pts2, M):

    # Scale the correspondence
    A = np.empty((pts1.shape[0],9))

    pts1 = pts1 / M
    pts2 = pts2 / M
    x1 = pts1[:,0]
    y1 = pts1[:,1]
    x2 = pts2[:,0]
    y2 = pts2[:,1]

    T = np.array([[1/M, 0, 0],
                  [0, 1/M, 0],
                  [0,  0,  1]])

    # Construct A matrix
    A = np.vstack((x2 * x1, x2 * y1 , x2, y2 * x1,  y2 * y1, y2, x1, y1, np.ones(pts1.shape[0]))).T


    u, s, vh = np.linalg.svd(A) # Find SVD of AtA
    F = vh[-1].reshape(3,3) # Fundamental Matrix is column corresponding to the least singular values

    F = helper.refineF(F, pts1, pts2) # Refine F by using local minimization

    # Enforce rank2 constraint a.k.a singularity condition
    F = helper._singularize(F)

    # Unscale the fundamental matrix
    F = np.dot((np.dot(T.T,F)) , T)

    return F


'''
Q2.2: Seven Point Algorithm
    Input:  pts1, Nx2 Matrix
            pts2, Nx2 Matrix
            M, a scalar parameter computed as max (imwidth, imheight)
    Output: Farray, a list of estimated fundamental matrix.
'''
def sevenpoint(pts1, pts2, M):

    A = np.empty((pts1.shape[0],9))

    pts1 = pts1 / M
    pts2 = pts2 / M
    x1 = pts1[:,0]
    y1 = pts1[:,1]
    x2 = pts2[:,0]
    y2 = pts2[:,1]

    T = np.array([[1/M, 0, 0],
                  [0, 1/M, 0],
                  [0,  0,  1]])

    # Construct A matrix
    A = np.vstack((x2 * x1, x2 * y1 , x2, y2 * x1,  y2 * y1, y2, x1, y1, np.ones(pts1.shape[0]))).T

    u, s, vh = np.linalg.svd(A) # Find SVD of AtA
    f1 = vh[-1].reshape(3,3) # Fundamental Matrix is column corresponding to the least singular values
    f2 = vh[-2].reshape(3,3)

    detF_func = lambda coeff: np.linalg.det(coeff*f1 + (1-coeff)*f2)

    a0 = detF_func(0)
    a1 = 2*(detF_func(1) - detF_func(-1))/3 - (detF_func(2)-detF_func(-2))/12
    a2 = (detF_func(1) + detF_func(-1))/2 - a0
    a3 = (detF_func(1) - detF_func(-1))/2 - a1

    coeff_sol = np.roots([a3,a2,a1,a0])

    F_mat = [coeff*f1 + (1-coeff)*f2 for coeff in coeff_sol]

    F_mat = [helper.refineF(F, pts1, pts2) for F in F_mat]

    # Unscale the fundamental matrix
    F = [np.dot((np.dot(T.T,F)) , T) for F in F_mat]

    return F


'''
Q3.1: Compute the essential matrix E.
    Input:  F, fundamental matrix
            K1, internal camera calibration matrix of camera 1
            K2, internal camera calibration matrix of camera 2
    Output: E, the essential matrix
'''
def essentialMatrix(F, K1, K2):

    E = np.dot((np.dot(K2.T ,F)), K1)

    return E

'''
Q3.2: Triangulate a set of 2D coordinates in the image to a set of 3D points.
    Input:  C1, the 3x4 camera matrix
            pts1, the Nx2 matrix with the 2D image coordinates per row
            C2, the 3x4 camera matrix
            pts2, the Nx2 matrix with the 2D image coordinates per row
    Output: P, the Nx3 matrix with the corresponding 3D points per row
            err, the reprojection error.
'''
def triangulate(C1, pts1, C2, pts2):
    x1 = pts1[:,0]
    y1 = pts1[:,1]
    x2 = pts2[:,0]
    y2 = pts2[:,1]
    w = np.empty((x1.shape[0],3))

    A1 = np.vstack([C1[0,0] - C1[2,0]*x1, C1[0,1] - C1[2,1]*x1, C1[0,2] - C1[2,2]*x1, C1[0,3] - C1[2,3]*x1]).T
    A2 = np.vstack([C1[1,0] - C1[2,0]*y1, C1[1,1] - C1[2,1]*y1, C1[1,2] - C1[2,2]*y1, C1[1,3] - C1[2,3]*y1]).T
    A3 = np.vstack([C2[0,0] - C2[2,0]*x2, C2[0,1] - C2[2,1]*x2, C2[0,2] - C2[2,2]*x2, C2[0,3] - C2[2,3]*x2]).T
    A4 = np.vstack([C2[1,0] - C2[2,0]*y2, C2[1,1] - C2[2,1]*y2, C2[1,2] - C2[2,2]*y2, C2[1,3] - C2[2,3]*y2]).T

    for i in range(x1.shape[0]):

        A = np.vstack((A1[i,:], A2[i,:], A3[i,:], A4[i,:]))
        u, s, vh = np.linalg.svd(A)
        wi_hom = vh[-1] # Nx4 vector
        wi  = wi_hom[0:3]/vh[-1,-1] # Nx3 vector
        w[i,:]  = wi

    w_hom = np.hstack((w,np.ones([w.shape[0],1])))

    # Reprojecting
    pts1_hat = np.dot(C1 , w_hom.T)
    pts2_hat = np.dot(C2 , w_hom.T)

    # pdb.set_trace()
    # Normalizing
    p1_hat_norm = (np.divide(pts1_hat[0:2,:] , pts1_hat[2,:])).T
    p2_hat_norm = (np.divide(pts2_hat[0:2,:] , pts2_hat[2,:])).T

    err1 = np.square(pts1[:,0] - p1_hat_norm[:,0]) + np.square(pts1[:,1] - p1_hat_norm[:,0])
    err2 = np.square(pts2[:,0] - p2_hat_norm[:,0]) + np.square(pts2[:,1] - p2_hat_norm[:,0])
    err = np.sum(err1) + np.sum(err2)

    return w,err
'''
Q4.1: 3D visualization of the temple images.
    Input:  im1, the first image
            im2, the second image
            F, the fundamental matrix
            x1, x-coordinates of a pixel on im1
            y1, y-coordinates of a pixel on im1
    Output: x2, x-coordinates of the pixel on im2
            y2, y-coordinates of the pixel on im2

'''
def epipolarCorrespondence(im1, im2, F, x1, y1):

    # Extract window from im1 around x1, y1
    rect_size = 10 # Size of the window

    # if np.abs(x1) >= rect_size//2 and np.abs(y1) >= rect_size//2:
    im1_sec = im1[(y1 - rect_size//2): (y1 + rect_size//2 + 1), (x1 - rect_size//2): (x1 + rect_size//2 + 1),:]  # Section of im1 around x1,y1


    im2_h, im2_w,_ = im2.shape # Size of im1

    pt1 = np.array([x1, y1, 1]) # homogeneous coordinates of im1

    ep_line = np.dot(F,pt1) # Epipolar Line
    ep2_l = ep_line / np.linalg.norm(ep_line)

    ep2_y = np.arange(im2_h) #np.arange(y1-rect_size//2,y1+rect_size//2,1) # search coordinates for im2

    ep2_x = np.rint(-(ep2_l[1]*ep2_y + ep2_l[2])/ep2_l[0])
    # pdb.set_trace()
    # Ensure that the image section lies within the image dimensions
    im_in = (ep2_y >= rect_size//2) & (ep2_y + rect_size//2 < im2_h ) & (ep2_x >= rect_size//2) & (ep2_x + rect_size//2 < im2_w )
    valid_y, valid_x = ep2_y[im_in], ep2_x[im_in] # im2 region for comparison

    # Gaussian weight distribution about the center
    std_dev = 2
    rect_vec = np.arange(-rect_size//2 , rect_size//2 + 1 ,1)
    rect_x, rect_y = np.meshgrid(rect_vec, rect_vec)

    gauss_wt = np.dot( (np.exp(-((rect_x**2 + rect_y**2) / (2 * (std_dev**2))))),1)
    gauss_wt = gauss_wt / np.sqrt(2*np.pi*std_dev**2)
    gauss_wt = np.sum(gauss_wt)
    err_val = np.inf

    for i in range(valid_x.shape[0]):

        im2_sec = im2[int(valid_y[i] - rect_size//2): int(valid_y[i] + rect_size//2 + 1), int(valid_x[i] - rect_size//2): int(valid_x[i] + rect_size//2 + 1),:]
        err = np.linalg.norm((im1_sec-im2_sec)*gauss_wt)

        if err < err_val:
            err_val = err
            y2 = valid_y[i]
            x2 = valid_x[i]

    return x2, y2



'''
Q5.1: RANSAC method.
    Input:  pts1, Nx2 Matrix
            pts2, Nx2 Matrix
            M, a scaler parameter
    Output: F, the fundamental matrix
            inliers, Nx1 bool vector set to true for inliers
'''
def ransacF(pts1, pts2, M, nIters, tol):
    max_iters = 100  # the number of iterations to run RANSAC for
    inlier_tol = 1e-2 # the tolerance value for considering a point to be an inlier
    max_inliers = -1
    F = np.empty([3,3]) #3 by 3 empty matrix for the best homograph

    rand_1 = np.empty([2,4])
    rand_2 = np.empty([2,4])
    max_inliers = -1

    x1 = pts1[:,0]
    y1 = pts1[:,1]
    x2 = pts2[:,0]
    y2 = pts2[:,1]

    pts1_hom = np.hstack((pts1,np.ones([pts1.shape[0],1])))
    pts2_hom = np.hstack((pts2,np.ones([pts1.shape[0],1])))

    for ind in range(max_iters):
        tot_inliers = 0
        ind_rand = np.random.choice(pts1.shape[0],7)

        rand_1 = pts1[ind_rand,:]
        rand_2 = pts2[ind_rand,:]

        F = eightpoint(rand_1, rand_2, M)

        pts2_pred = np.dot(F,pts1_hom)

        err = np.linalg.norm(pts2_hom - pts2_pred)

        inliers_num = err < inlier_tol
        tot_inliers[inliers_num]
        if tot_inliers > max_inliers:
            bestF = F
            max_inliers = tot_inliers
            inliers = inliers_num


    return bestF, inliers
'''
Q5.2: Rodrigues formula.
    Input:  r, a 3x1 vector
    Output: R, a rotation matrix
'''
def rodrigues(r):

    R = np.empty(3,3)
    theta = np.linalg.norm(r)

    if np.abs(theta) < 1e-2:
        R = np.eye(3)

    else:
        u = r/theta
        u_x = np.array([0, -u[2], u[1]],[u[2], 0, -u[0]],[-u[1],u[0],0])
        R = np.eye(3)*np.cos(theta) +  (1-np.cos(theta))*(np.dot(u,u.T)) + u_x*np.sin(theta)

    return R
'''
Q5.2: Inverse Rodrigues formula.
    Input:  R, a rotation matrix
    Output: r, a 3x1 vector
'''
def invRodrigues(R):
    zero_tol = 1e-2
    A = (R - R.T)/2
    rho = np.array([[A[2,1]],[A[0,2]],[A[1,0]]])
    s = np.linalg.norm(rho)
    c = (np.trace(R) -1)/2

    if s < zero_tol & c==1:
        r = np.zeros((3,1))

    elif s < zero_tol & c == -1:
        v_tmp = R + np.eye(3)
        for i in range(R.shape[0]):
            if np.sum(v_tmp[:,i]) !=0:
                v = v_tmp[:,i]
                break

        u = v/np.linalg.norm(v)
        u_pi = u*np.pi
        print(u_pi.shape)

        if (np.linalg.norm(u_pi) == np.pi) & ((np.abs(u_pi[0]) < zero_tol & np.abs(u_pi[1]) < zero_tol & u_pi[2] < 0) | (np.abs(u_pi[0])< zero_tol & u_pi[1] < zero_tol) |(u_pi[0] < zero_tol)):
            r = -u_pi

        else:
            r = u_pi


    else:
        u = rho/s
        theta = np.arctan2(s,c)
        r = u*theta

    return r


'''
Q5.3: Rodrigues residual.
    Input:  K1, the intrinsics of camera 1
            M1, the extrinsics of camera 1
            p1, the 2D coordinates of points in image 1
            K2, the intrinsics of camera 2
            p2, the 2D coordinates of points in image 2
            x, the flattened concatenationg of P, r2, and t2.
    Output: residuals, 4N x 1 vector, the difference between original and estimated projections
'''
def rodriguesResidual(K1, M1, p1, K2, p2, x):
    # Replace pass by your implementation
    pass

'''
Q5.3 Bundle adjustment.
    Input:  K1, the intrinsics of camera 1
            M1, the extrinsics of camera 1
            p1, the 2D coordinates of points in image 1
            K2,  the intrinsics of camera 2
            M2_init, the initial extrinsics of camera 1
            p2, the 2D coordinates of points in image 2
            P_init, the initial 3D coordinates of points
    Output: M2, the optimized extrinsics of camera 1
            P2, the optimized 3D coordinates of points
'''
def bundleAdjustment(K1, M1, p1, K2, M2_init, p2, P_init):
    # Replace pass by your implementation
    pass
'''
Q6.1 Multi-View Reconstruction of keypoints.
    Input:  C1, the 3x4 camera matrix
            pts1, the Nx3 matrix with the 2D image coordinates and confidence per row
            C2, the 3x4 camera matrix
            pts2, the Nx3 matrix with the 2D image coordinates and confidence per row
            C3, the 3x4 camera matrix
            pts3, the Nx3 matrix with the 2D image coordinates and confidence per row
    Output: P, the Nx3 matrix with the corresponding 3D points for each keypoint per row
            err, the reprojection error.
'''
def MultiviewReconstruction(C1, pts1, C2, pts2, C3, pts3, Thres):
    # Replace pass by your implementation
    pass


if __name__ == "__main__":
    # 2.1
    pts = np.load('../data/some_corresp.npz')
    pts1 = pts['pts1']
    pts2 = pts['pts2']
    im1 = plt.imread('../data/im1.png')
    im2 = plt.imread('../data/im2.png')
    M = np.max(im1.shape)

    F = sevenpoint(pts1[1:7,:], pts2[1:7,:], M) # EightPoint algrithm to find F

    # F = eightpoint(pts1, pts2, M) # EightPoint algrithm to find F
    # np.savez('q2_1.npz', F, M)
    # # helper.displayEpipolarF(im1, im2, F) # Visualize result

    # # 3.1
    # # import camera instrinsics
    # K = np.load('../data/intrinsics.npz')
    # K1 = K['K1']
    # K2 = K['K2']
    # E = essentialMatrix(F, K1, K2)

    # # 4.1
    # x2, y2 = epipolarCorrespondence(im1, im2, F, x1, y1)
    # # helper.epipolarMatchGUI(im1, im2, F)
