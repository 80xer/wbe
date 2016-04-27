# -*- coding: utf-8 -*-
import sys, scipy, pandas, math
import numpy as np
import statsmodels.tsa.stattools as ts

reload(sys)
sys.setdefaultencoding('utf-8')
from scipy.interpolate import interp1d

class NtsCaldulator():       

    # 호출하는 프로시저
    def cal_nts_total(self, total_set_df, iv_info_dict, intv, thres_cut, dv_thres, lag_cut, dv_dir):
        
        dv = total_set_df['DV'].tolist()        
        #dv_crisis_digit_list, thres = self.get_dv_crisis_info(dv, 1, True) # 종속변수 위기 여부와 관련해서는 본 함수를 수정하면 된다.
        dv_crisis_digit_list, thres = self.get_dv_crisis_info_specific_value(dv, dv_thres, dv_dir)

        for c in total_set_df.columns:
            if c != 'DV' and c != 'YYYYMM' and c != 'DATE':
                 iv_info_dict[c].update(self.cal_nts(dv, total_set_df[c].tolist(), dv_crisis_digit_list, 30, intv, thres_cut, lag_cut))
                #(2016.03.10) nts 계산에서 선행기간 내 위기식별 구간 제한 추가작업 lag_cut

        return dv_crisis_digit_list, thres # 종속변수 위기여부 리스트, 임계치 반환
     
    def cal_nts(self, dv, iv, dv_crisis_digit, intv_cnt, intv, thres_cut, lag_cut):
        """
        iv 의 최대값 최소값을 intv_cnt 개수 구간으로 잘라서 모든 구간에 대하여 nts를 구하여
        가장 낮은 NTS 값을 갖는 intv를 반환한다
        """        
        iv_max = np.percentile(iv, (1-thres_cut)*100)        
        iv_min = np.percentile(iv, (thres_cut*100))
        intv_value = float(iv_max-iv_min) / float(intv_cnt)

        # thres 후보군 구하기
        thres_candidate = []
        #thres_candidate.append(iv_min)

        for i in range(intv_cnt+1):
            thres_candidate.append(iv_min + intv_value * float(i))
                    
        nts_list_up = {}
        nts_list_dn = {}

        for thres in thres_candidate:
            iv_digit_up, iv_digit_dn = self.get_iv_crisis_info(iv, thres)
            nts_list_up[thres] = self.cal_nts_by_digit(iv_digit_up, dv_crisis_digit, intv, lag_cut)
            nts_list_dn[thres] = self.cal_nts_by_digit(iv_digit_dn, dv_crisis_digit, intv, lag_cut)
            #(2016.03.10) nts 계산에서 선행기간 내 위기식별 구간 제한 추가작업

        up_min = min(nts_list_up.items(), key=lambda x: x[1])
        dn_min = min(nts_list_dn.items(), key=lambda x: x[1])

        nts_info = {}
        if up_min[1][0] < dn_min[1][0]:
            nts_info.update(up_min[1][1])
            nts_info['dir'] = 'U'
            nts_info['thres'] = up_min[0]
            nts_info['nts'] = up_min[1][0]            
        else:
            nts_info.update(dn_min[1][1])
            nts_info['dir'] = 'D'
            nts_info['thres'] = dn_min[0]
            nts_info['nts'] = dn_min[1][0]

        return nts_info
     
    # 독립변수의 thres와 방향성을 입력 받고 위기 digit series를 반환
    def get_iv_crisis_info(self, iv, thres):
        crisis_digit_up = []
        crisis_digit_down = []
        for d in iv:
            if d > thres:
                crisis_digit_up.append(True)
            else:
                crisis_digit_up.append(False)
        for d in iv:
            if d < thres:
                crisis_digit_down.append(True)
            else:
                crisis_digit_down.append(False)
        return crisis_digit_up, crisis_digit_down

    
    # iv_digit : 독립변수 위기여부 시계열
    # dv_digit : 종속변수 위기여부 시계열
    # intv     : 위기 유효 발생 기간
    def cal_nts_by_digit(self, iv_digit, dv_digit, intv, lag_cut):    #(2016.03.10) nts 계산에서 선행기간 내 위기식별 구간 제한 추가작업 lag_cut
        a = 0
        b = 0
        c = 0
        d = 0
        for i in range(len(iv_digit)-intv):     # 독립변수 시계열에서 선행기간 len 만큼 마이너스 (쉬프팅 효과)
            issue_crisis = False
            for j in range(lag_cut):
            #for j in range(12):                           # 이걸로 바꾸면 선행기간 내 발생을 제한함 2016.03.10 작업으로 불필요
                if dv_digit[i+j+1] == True:
                    issue_crisis = True

            if issue_crisis == True and iv_digit[i] == True:      # right signal
                a = a+1
            elif issue_crisis == True and iv_digit[i] == False:   # missed calls
                c = c+1
            elif issue_crisis == False and iv_digit[i] == True:   # false alarms
                b = b+1
            elif issue_crisis == False and iv_digit[i] == False:  # noise
                d = d+1
        if a == 0 or (b == 0 and d == 0):
            nts = 100
        else:
            nts = float(b)/(float(b) + float(d))*(float(a)+float(c))/float(a)
        info = {}
        info['nts'] = nts
        info['a'] = a                
        info['b'] = b
        info['c'] = c
        info['d'] = d
        return nts, info

    def get_dv_crisis_info(self, dv, alpha, dir_up=True):
        mean = np.average(dv)
        stdev = np.std(dv)
        if dir_up : # 위로 갈 수록 위기
            thres = mean + alpha * stdev
        else :      # 아래로 갈 수록 위기
            thres = mean - alpha * stdev
        crisis_digit = []
        for d in dv:
            if dir_up:
                if d > thres:
                    crisis_digit.append(True)
                else:
                    crisis_digit.append(False)
            else:
                if d < thres:
                    crisis_digit.append(True)
                else:
                    crisis_digit.append(False)
        return crisis_digit, thres

    def get_dv_crisis_info_specific_value(self, dv, thres, dir_up="U"):
        crisis_digit = []
        for d in dv:
            if dir_up == "U":
                if d > thres:
                    crisis_digit.append(True)
                else:
                    crisis_digit.append(False)
            else:
                if d < thres:
                    crisis_digit.append(True)
                else:
                    crisis_digit.append(False)
        return crisis_digit, thres
    
    def get_iv_sh_digit(self, df_iv_sh, iv_info, dv_thres, dv_dir):
        df_iv_sh_digit = df_iv_sh.copy()
        for i in df_iv_sh.index:
            columns = df_iv_sh.columns
            for col in columns:
                if col != 'DV' and col != 'DATE' and col != 'YYYYMM':      
                    thres = iv_info[col]['thres']
                    dir = iv_info[col]['dir']
                    if dir == 'U':
                        if df_iv_sh[col][i] >= thres:
                            df_iv_sh_digit.set_value(i, col, 1)
                        else:
                            df_iv_sh_digit.set_value(i, col, 0)
                    elif dir == 'D':
                        if df_iv_sh[col][i] <= thres:
                            df_iv_sh_digit.set_value(i, col, 1)
                        else:
                            df_iv_sh_digit.set_value(i, col, 0)
                elif col == 'DV':
                    if dv_dir == 'U':
                        if df_iv_sh[col][i] >= dv_thres:
                            df_iv_sh_digit.set_value(i, col, 1)
                        else:
                            df_iv_sh_digit.set_value(i, col, 0)
                    elif dv_dir == 'D':
                        if df_iv_sh[col][i] <= dv_thres:
                            df_iv_sh_digit.set_value(i, col, 1)
                        else:
                            df_iv_sh_digit.set_value(i, col, 0)

        return df_iv_sh_digit