# -*- coding: utf-8 -*-
import sys, scipy, pandas, math
import numpy as np
import statsmodels.tsa.stattools as ts
from statsmodels.tsa.filters import hp_filter
import statsmodels.api as sm
from matplotlib.mlab import PCA as mlabPCA
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d

reload(sys)
sys.setdefaultencoding('utf-8')


class HpFilter():
    # 입력받은 dataframe
    def run(self, x, param):
        #cycle, trend = hpfilter(x, 129600)
        cycle, trend = sm.tsa.filters.hpfilter(x, param)
        return cycle, trend
