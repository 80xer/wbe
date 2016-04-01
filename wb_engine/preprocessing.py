# -*- coding: utf-8 -*-
import sys, scipy, pandas, math
import numpy as np
import statsmodels.tsa.stattools as ts
from wb_engine.filter import HpFilter

reload(sys)
sys.setdefaultencoding('utf-8')
from scipy.interpolate import interp1d

class PreProcessing():

    def __init__(self):            
         pass

    # x와 y로 피팅하여 new_x에 대한 새로운 y 반환
    def get_interpolated_y(self, x, y, new_x):
        f = scipy.interpolate.interp1d(x, y, kind='cubic')
        return f(new_x)

    # 시계열 x에 대한 adf 테스트 결과 반환
    def get_adf_test(self, x, p):
        result = ts.adfuller(x)
        pvalue = result[1]                
        if pvalue < p :
            test_result = True
        else:
            test_result = False
        return test_result, pvalue

    # df 시계열에 대해서 adf 테스트를 수행한 후, 통과하지 못한 시계열에 대해서 차분
    # df 의 전반적인 시계열 길이가 1 축소
    def get_adf_test_after_df(self, df, df_out, iv_info_dict):        

        df = df.sort_values('DATE', ascending=[1]) # 정렬한번 하고 시작
        df_out = df_out.sort_values('DATE', ascending=[1])
                
        columns = df.columns
        col_data = columns[2:]
        for col in col_data:
            series = df[col]
            series_out = df_out[col]
                        
            adf_result, p = self.get_adf_test(series.tolist(), 0.10)
            #print 'col:%s|adf_result:%s|pvalue:%s'%(col,adf_result,p)
            
            if adf_result == False: # 데이터 차분
                new_series = self.get_diff_series(series, iv_info_dict)
                new_series_out = self.get_diff_series(series_out, iv_info_dict)

                df[col] = new_series
                df_out[col] = new_series_out

                iv_info_dict[col]['adf_test'] = False                
            else:                   # 있는 데이터 그대로 사용
                iv_info_dict[col]['adf_test'] = True
        
        df = df[1:].reset_index(drop=True)
        df_out = df_out[1:].reset_index(drop=True)
        
        return df, df_out

    # df 시계열에 대해서 adf 테스트를 수행한 후, 통과하지 못한 시계열에 대해서 차분
    # df 의 전반적인 시계열 길이가 1 축소
    def get_hp_filter(self, df, param):        

        df = df.sort_values('DATE', ascending=[1]) # 정렬한번 하고 시작
        hp = HpFilter()
        columns = df.columns
        col_data = columns[2:]
        for col in col_data:
            series = df[col].tolist()
            c, t = hp.run(series, param)
            df[col] = t

        return df

    def get_diff_series(self, series, in_info_dict):

        d = series.tolist()
        new_data = []
        new_data.append(0)

        for i in range(len(d))[1:]:
            new_data.append(d[i] - d[i-1])
        
        new_series = pandas.Series(new_data)
        return new_series

    def scale_iv(self, df, df_out):
        columns = df.columns
        col_data = columns[2:]
        for col in col_data:
            d = df[col]
            d_out = df_out[col]
            mean = np.average(d)
            stdev = np.std(d)
            df[col] = (d - mean) / stdev
            df_out[col] = (d_out - mean) / stdev

        return df, df_out

    def time_shift(self, df_dv, intv):      
        cols = df_dv.columns
        l = len(df_dv)
        s0 = pandas.Series(df_dv[cols[0]][:l-intv].tolist()) # date
        s1 = pandas.Series(df_dv[cols[1]][:l-intv].tolist()) # date2
        s2 = pandas.Series(df_dv[cols[2]][intv:].tolist())
        df_new = pandas.DataFrame()
        df_new[cols[0]] = s0
        df_new[cols[1]] = s1
        df_new[cols[2]] = s2
        return df_new

