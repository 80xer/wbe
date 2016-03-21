# -*- coding: utf-8 -*-
import sys, scipy, pandas, math
import numpy as np
import statsmodels.tsa.stattools as ts
from matplotlib.mlab import PCA as mlabPCA
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d

reload(sys)
sys.setdefaultencoding('utf-8')


class PcaCalculator():

    # 입력받은 dataframe
    def run_cap(self, iv_df, iv_df_out, coverage):
        array = iv_df.as_matrix()
        mlab_pca = mlabPCA(array)
        
        """
        a a centered unit sigma version of input a
        numrows, numcols: the dimensions of a
        mu : a numdims array of means of a. This is the vector that points to the origin of PCA space.
        sigma : a numdims array of standard deviation of a
        fracs : the proportion of variance of each of the principal components
        s : the actual eigenvalues of the decomposition
        Wt : the weight vector for projecting a numdims point or array into PCA space
        Y : a projected into PCA space
        """
        y = mlab_pca.Y
        wt = mlab_pca.Wt
        eigenvalues = mlab_pca.s
        mu = mlab_pca.mu
        fracs = mlab_pca.fracs        

        cover_idx = []
        sum = 0
        cnt = 0

        #검증
        y[0][0]
        sum2= 0.0
        sum3= 0.0
        for i in range(len(wt[0])): # 첫번째 팩터
            
            sum2 += wt[0][i] * iv_df.get_value(0, iv_df.columns.tolist()[i])
            sum3 += wt[0][i] * iv_df_out.get_value(0, iv_df_out.columns.tolist()[i])
            
            print "%s|%s|%s"%(iv_df.columns.tolist()[i], wt[0][i], iv_df.get_value(0, iv_df.columns.tolist()[i]))
            print "%s|%s|%s"%(iv_df_out.columns.tolist()[i], wt[0][i], iv_df_out.get_value(0, iv_df_out.columns.tolist()[i]))

        
        df = pandas.DataFrame()
        for f in fracs:
            sum = sum + f
            if sum > coverage:
                break
            cover_idx.append(cnt)
            df["FAC%s"%(cnt)] = y.T[cnt]
            cnt = cnt + 1

        df_out = pandas.DataFrame()
        for i in cover_idx:
            factor_cd = "FAC%s"%(i)
            for j in range(len(iv_df_out)):
                col_idx = 0
                value = 0.0
                for t in range(len(iv_df_out.columns)):
                    value += iv_df_out.get_value(j, iv_df.columns.tolist()[t]) * wt[i][t]
                    col_idx += 1
                df_out.set_value(j, factor_cd, value)


        y = y.T[:cnt].tolist()
        wt = wt[:cnt].tolist()

        return y, wt, fracs, df, df_out
        


def test():
    np.random.seed(234234782) # random seed for consistency

    # A reader pointed out that Python 2.7 would raise a
    # "ValueError: object of too small depth for desired array".
    # This can be avoided by choosing a smaller random seed, e.g. 1
    # or by completely omitting this line, since I just used the random seed for
    # consistency.

    mu_vec1 = np.array([0,0,0])
    cov_mat1 = np.array([[1,0,0],[0,1,0],[0,0,1]])
    class1_sample = np.random.multivariate_normal(mu_vec1, cov_mat1, 20).T
    assert class1_sample.shape == (3,20), "The matrix has not the dimensions 3x20"

    mu_vec2 = np.array([1,1,1])
    cov_mat2 = np.array([[1,0,0],[0,1,0],[0,0,1]])
    class2_sample = np.random.multivariate_normal(mu_vec2, cov_mat2, 20).T
    assert class1_sample.shape == (3,20), "The matrix has not the dimensions 3x20"

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')
    plt.rcParams['legend.fontsize'] = 10
    ax.plot(class1_sample[0,:], class1_sample[1,:],\
        class1_sample[2,:], 'o', markersize=8, color='blue', alpha=0.5, label='class1')
    ax.plot(class2_sample[0,:], class2_sample[1,:],\
        class2_sample[2,:], '^', markersize=8, alpha=0.5, color='red', label='class2')

    plt.title('Samples for class 1 and class 2')
    ax.legend(loc='upper right')
    plt.show()

    all_samples = np.concatenate((class1_sample, class2_sample), axis=1)
    assert all_samples.shape == (3,40), "The matrix has not the dimensions 3x40"

    mean_x = np.mean(all_samples[0,:])
    mean_y = np.mean(all_samples[1,:])
    mean_z = np.mean(all_samples[2,:])

    mean_vector = np.array([[mean_x],[mean_y],[mean_z]])

    print('Mean Vector:\n', mean_vector)

    scatter_matrix = np.zeros((3,3))
    for i in range(all_samples.shape[1]):
        scatter_matrix += (all_samples[:,i].reshape(3,1)\
            - mean_vector).dot((all_samples[:,i].reshape(3,1) - mean_vector).T)
    print('Scatter Matrix:\n', scatter_matrix)

    cov_mat = np.cov([all_samples[0,:],all_samples[1,:],all_samples[2,:]])
    print('Covariance Matrix:\n', cov_mat)
    
    mlab_pca = mlabPCA(all_samples.T)

    print('PC axes in terms of the measurement axes'\
            ' scaled by the standard deviations:\n',\
              mlab_pca.Wt)

    plt.plot(mlab_pca.Y[0:20,0],mlab_pca.Y[0:20,1], 'o', markersize=7,\
            color='blue', alpha=0.5, label='class1')
    plt.plot(mlab_pca.Y[20:40,0], mlab_pca.Y[20:40,1], '^', markersize=7,\
            color='red', alpha=0.5, label='class2')

    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.xlim([-4,4])
    plt.ylim([-4,4])
    plt.legend()
    plt.title('Transformed samples with class labels from matplotlib.mlab.PCA()')

    plt.show()