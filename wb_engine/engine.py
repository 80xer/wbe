# -*- coding: utf-8 -*-
import sys, locale, wb_engine.read, datetime, os
from wb_engine.utility import DateUtility
from wb_engine.io import IO
from wb_engine.preprocessing import PreProcessing
from wb_engine.nts import NtsCaldulator
from wb_engine.pca import PcaCalculator
from operator import itemgetter
from wb_engine.io_template import IoTemplate
from wb_engine.db import dbHelper
import copy

reload(sys)
sys.setdefaultencoding('utf-8')


class WbEngine:
    def __init__(self):
        return

    def run(self, params, options):

        t0 = params['t0']   # 초기   날짜 세팅
        t1 = params['t1']   # 마지막 날짜 세팅

        iv_total = []

        # 엑셀에서 독립변수 받기
        read_module = wb_engine.read.ReadModule(t0, t1)  # 읽기 모듈 객체화
        input_path = os.getcwd() + "\\input"            # input file 경로 설정
        iv_path = input_path + u"\\iv\\"                # 독립변수 파일 경로 /iv 세팅
        paths = os.listdir(iv_path)                     # 독립변수 파일 경로 /iv 내 파일 리스트 가지고 오기

        for path in paths:                              # 개발중이므로 한 파일만 읽는다.
            full_path = iv_path + path
            iv_total.extend(read_module.read_file(full_path))

        # 디비에서 독립변수 받기
        # qr = wb_engine.db.queries(t0, t1)                       # 쿼리 로직 객체화
        # items = qr.getItems(options.userId, options.seq)   # 유저 셋팅 아이템 받기
        # iv_total.extend(items)

        # 인풋 모두 I 이므로 의미 없어서 주석처리.
        # iv_total_new = []
        # for iv in iv_total:
        #     if iv.io_type == 'I':
        #         iv_total_new.append(iv)
        #     else:
        #         sys.exit()
        # iv_total = iv_total_new

        # debug 용 데이터 축소
        if options.debug:
            iv_total = iv_total[:12]
            print "length of iv_total is %s" %len(iv_total)

        # 독립변수별 코드 <--> 이름 Dictionary 세팅                    
        iv_code = {}
        for iv in iv_total:
            iv_code[iv.code] = iv.name

        # 엑셀에서 종속변수 받기
        dv_1 = read_module.read_file(input_path + u"\\dv.xlsx")

        # 디비에서 종속변수 받기
        # dv_1 = qr.getDv()

        du = DateUtility()

        # t0와 t1 월별날짜 리스트 계산
        month_list_str, month_list_months = du.get_montly_span(t0, t1)

        # # 시계열 조정
        # iv_total = wb_engine.read.revision_date(iv_total, month_list_str)

        iv_total_out = copy.deepcopy(iv_total)

        iv_info_dict = {}
        for iv in iv_total:
            iv.set_monthly_data()  #같은월에 여러 데이터중 최신 데이터만
            # 내삽
            iv.set_interpolated_data(month_list_months, month_list_str)
            iv_info_dict[iv.code] = {}
            iv_info_dict[iv.code]['group'] = iv.group

        # out of sample months -------------------------------------------------
        month_list_str_out, month_list_months_out = du.get_montly_span(t0, params['t2'])
        for iv in iv_total_out:
            iv.set_monthly_data()
            iv.set_interpolated_data(month_list_months_out, month_list_str_out)
        # ----------------------------------------------------------------------

        dv_1[0].set_monthly_data()
        dv_1[0].set_interpolated_data(month_list_months, month_list_str)

        dv_1_out = copy.deepcopy(dv_1)
        dv_1_out[0].set_monthly_data()
        dv_1_out[0].set_interpolated_data(month_list_months_out, month_list_str_out)

        # 월중 최신데이터만 선택, 내삽 완료.

        df_iv = wb_engine.read.convert_series_list_to_dataframe(iv_total)

        # out of sample months ---------------------------------------------------------------
        df_iv_out = wb_engine.read.convert_series_list_to_dataframe(iv_total_out)
        # ------------------------------------------------------------------------------------

        io = IO()
        io.print_df('df', df_iv)
        io.print_dict('code_mapper', iv_code)

        # 전처리 작업 구동
        pp = PreProcessing()

        # 독립변수
        io.print_df('df_iv', df_iv)

        # ADF 테스트 후 차분
        df_iv, df_iv_out = pp.get_adf_test_after_df(df_iv, df_iv_out, iv_info_dict) # 시계열 길이 하나 줄어들음.

        # out of sample months ---------------------------------------------------------------
        # df_iv_out = pp.get_adf_test_after_df(df_iv_out, iv_info_dict) # 시계열 길이 하나 줄어들음.
        # ------------------------------------------------------------------------------------

        # Hp Filter
        df_iv = pp.get_hp_filter(df_iv, params['hp_filter'])

        # out of sample months ---------------------------------------------------------------
        df_iv_out = pp.get_hp_filter(df_iv_out, params['hp_filter'])
        # ------------------------------------------------------------------------------------

        # io.print_df('df_iv', df_iv)
        # df_iv = pp.scale_iv(df_iv)

        # 종속변수
        df_dv = wb_engine.read.convert_series_list_to_dataframe(dv_1)
        df_dv_out = wb_engine.read.convert_series_list_to_dataframe(dv_1_out)

        df_dv = df_dv[1:].reset_index(drop=True) # 맨 앞 데이터 차분
        df_dv_out = df_dv_out[1:].reset_index(drop=True)

        io.print_df('df_dv', df_dv)

        # there is no need to shift timelie changing definition of crisis to "within"
        # 변수 shifting
        # df_dv_sh = pp.time_shift(df_dv, params['intv']) # 여기가 문제
        # df_iv_sh = df_iv[:len(df_iv)-params['intv']]
        df_iv_sh = df_iv
        df_iv_sh_out = df_iv_out

        if params['scaling'] == '1':
            df_iv_sh, df_iv_sh_out = pp.scale_iv(df_iv_sh, df_iv_sh_out)

        df_iv_sh['DV'] = df_dv[df_dv.columns[2]]
        df_iv_sh_out['DV'] = df_dv_out[df_dv_out.columns[2]] # out of sample

        # nts 계산
        nts_module = NtsCaldulator()
        dv_crisis_digit_list, dv_thres = nts_module.cal_nts_total(df_iv_sh, iv_info_dict, params['intv'], params['thres_cut'], params['dv_thres'], params['lag_cut'])
        # iv_info_dict 에 nts 관련 정보 적재  (2016.03.10) nts 계산에서 선행기간 내 위기식별 구간 제한 추가작업 lag_cut
        # nts_module.cal_nts_by_digit(df_iv_sh, dv_crisis_digit_list)
        io.print_nts_info(iv_info_dict, 'iv_info')

        # nts 에 따른 thres와 digit 저장
        df_iv_sh_digit = nts_module.get_iv_sh_digit(df_iv_sh, iv_info_dict, params['dv_thres'], params['dv_dir'])

        srted = sorted(iv_info_dict.iteritems(), key=self.get_value, reverse=False)
        filtered = [s for s in srted if s[1]['nts'] < params['nts_thres']]
        # filtered = srted[:149]

        code_list = []
        for f in filtered :
            code_list.append(f[0])

        df_iv_flt = df_iv_sh[code_list]
        df_iv_flt_out = df_iv_sh_out[code_list] # out of sample

        io.print_df('df_iv_flt', df_iv_flt)

        pca_module = PcaCalculator()

        y, wt, fracs, df_factor, df_factor_out = pca_module.run_cap(df_iv_flt, df_iv_flt_out, params['pca_thres'])

        factor_weight = {}
        factor_weight['col_list'] = df_iv_flt.columns.tolist()
        factor_weight['weight'] = wt
        factor_weight['fracs'] = fracs

        # df_factor_yyyymm 출력용
        df_factor_series = df_factor.copy()
        df_factor_series['YYYYMM'] = df_iv_sh['YYYYMM'].tolist()
        df_factor_series['DV'] = df_iv_sh['DV'].tolist()
        io.print_df('factor', df_factor)

        # df_factor_yyyymm 출력용
        df_factor_series_out = df_factor_out.copy()
        df_factor_series_out['YYYYMM'] = df_iv_sh_out['YYYYMM'].tolist()
        df_factor_series_out['DV'] = df_iv_sh_out['DV'].tolist()

        factor_info_dict = {}
        for col in df_factor.columns:
            factor_info_dict[col] = {}

        # df_factor['DV'] = df_dv_sh[df_dv_sh.columns[2]]
        nts_module.cal_nts_total(df_factor_series, factor_info_dict, params['intv'], params['thres_cut'], params['dv_thres'] , params['lag_cut'])
        # (2016.03.10) nts 계산에서 선행기간 내 위기식별 구간 제한 추가작업 lag_cut

        for i in range(len(df_factor.columns.tolist())):
            factor_info_dict[df_factor.columns.tolist()[i]]['weight'] = factor_weight['fracs'][i]

        # 위기지수 계산
        df_warning_idx = self.cal_warning_idx(factor_info_dict, df_factor_series)
        df_warning_idx_out = self.cal_warning_idx(factor_info_dict, df_factor_series_out)

        result = {}
        result['params'] = params
        result['iv_raw'] = iv_total
        result['iv_code'] = iv_code
        result['iv_info_dict'] = iv_info_dict
        result['df_iv_sh'] = df_iv_sh
        result['df_iv_sh_digit'] = df_iv_sh_digit
        result['factor_info_dict'] = factor_info_dict
        result['df_factor_yyyymm'] = df_factor_series
        result['df_warning_idx'] = df_warning_idx
        result['df_warning_idx_out'] = df_warning_idx_out
        result['dv_thres'] = dv_thres
        result['factor_weight'] = factor_weight

        return result

    def get_value(self, item):
        return item[1]['nts']

    def list_to_dict(self, list):
        result = {}
        for i in range(len(list)):
             result[list[i][0]] = list[i][1]
        return result

    def cal_warning_idx(self, factor_info_dict, df_factor_series):

        # NTS 가 0일경우 위기지수 계산시 division by 0 에러가 발생하므로
        # NTS 가 0일경우 NTS가 0이 아닌 NTS들의 최소값으로 대체하여 계산한다.
        nts_list = []
        for k, v in factor_info_dict.iteritems():
            nts_list.append(v['nts'])
        nts_min = min(nts_list)

        factor_info_dict_2 = factor_info_dict.copy()
        weight_sum = 0.0
        for k, v in factor_info_dict_2.iteritems():
            if v['nts'] == 0:
                v['weight'] = 1/nts_min
            else:
                v['weight'] = 1/v['nts']
            weight_sum += v['weight']

        df_warning_idx = df_factor_series.copy()
        for i in df_warning_idx.index:
            idx_sum = 0.0
            for k, v in factor_info_dict_2.iteritems():
                dir = v['dir']
                thres = v['thres']
                nts = v['nts']
                if dir == 'up' :
                    if df_warning_idx[k][i] > thres:
                        idx_sum += v['weight'] * 1.0
                elif dir == 'down':
                    if df_warning_idx[k][i] < thres:
                        idx_sum += v['weight'] * 1.0
            warning_idx = idx_sum / weight_sum
            df_warning_idx.set_value(i, 'IDX', warning_idx)

        return df_warning_idx

