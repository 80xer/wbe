# -*- coding: utf-8 -*-
import sys, xlrd, datetime, calendar, os, csv, json, math
reload(sys)
sys.setdefaultencoding('utf-8')
from wb_engine.read import Series
from jinja2 import Environment, Template, PackageLoader


class IoTemplate():

    def __init__(self): # SERIES 출력
        pass

    def make_report(self, data):

        # 초기화면
        self.write_index(data['params'], data['iv_info_dict'], data['iv_code'], data['df_warning_idx'])

        # 독립변수별 정보
        self.write_iv_info(data['iv_info_dict'], data['iv_code'])
        for k, v in data['iv_info_dict'].iteritems():
            self.write_iv_ts(k, data['df_iv_sh'], data['iv_info_dict'], data['iv_code'])

        # 독립변수별 정보(차트)
        self.write_iv_info_chart(data['iv_info_dict'], data['df_iv_sh'], data['iv_code'])
        
        # 팩터별 정보
        self.write_factor_info(data['factor_info_dict'])
        for k, v in data['factor_info_dict'].iteritems():
            self.write_factor_ts(k, data['df_factor_yyyymm'], data['factor_info_dict'], data['iv_code'])


    def write_index(self, params, iv_info, iv_code, df_warning_idx):
        
        env = Environment(loader=PackageLoader('wb_engine', 'report/templates'))
        path = os.getcwd() + "\\wb_engine\\report\\"
        template = env.get_template("index.html")

        chart_idx = df_warning_idx['IDX'].tolist();        
        for i in range(len(chart_idx)):
            chart_idx[i] = round(chart_idx[i], 4)
        chart_idx = json.dumps(chart_idx)

        chart_dv = df_warning_idx['DV'].tolist()
        for i in range(len(chart_dv)):
            chart_dv[i] = round(chart_dv[i], 4)
        chart_dv = json.dumps(chart_dv)
        

        chart_yyyymm = json.dumps(df_warning_idx['YYYYMM'].tolist())               

        temp = template.render(params=params, iv_info=iv_info, iv_code=iv_code, chart_idx=chart_idx, chart_dv=chart_dv, chart_yyyymm=chart_yyyymm)
        with open(path + "index.html", "wb") as fh:
            fh.write(temp)
    
    def write_iv_info(self, iv_info, iv_code):
        env = Environment(loader=PackageLoader('wb_engine', 'report/templates'))
        path = os.getcwd() + "\\wb_engine\\report\\"
        template = env.get_template("iv_info.html")
        temp = template.render(iv_info=iv_info, iv_code=iv_code)
        with open(path + "report_iv_info.html", "wb") as fh:
            fh.write(temp)

    def write_factor_info(self, factor_info):
        env = Environment(loader=PackageLoader('wb_engine', 'report/templates'))
        path = os.getcwd() + "\\wb_engine\\report\\"
        template = env.get_template("factor_info.html")
        temp = template.render(factor_info=factor_info)
        with open(path + "report_factor_info.html", "wb") as fh:
            fh.write(temp)

    def write_iv_info_chart(self, iv_info, df_iv, iv_code):
        # iv_info에 차트용 데이터를 추가한다
        for k, v in iv_info.iteritems():
            date_list = df_iv['YYYYMM'].tolist()
            iv_ts = df_iv[k].tolist()
            dv_ts = df_iv['DV'].tolist()
            v['iv_ts'] = json.dumps(iv_ts)
            v['dv_ts'] = json.dumps(dv_ts)
            v['date'] = json.dumps(date_list) 

        env = Environment(loader=PackageLoader('wb_engine', 'report/templates'))
        path = os.getcwd() + "\\wb_engine\\report\\"        
        template = env.get_template("iv_info_chart.html")
        temp = template.render(iv_info=iv_info, iv_code=iv_code)

        with open(path + "report_iv_info_chart.html", "wb") as fh:
            fh.write(temp)

    # 팩터 정보 + 차트
    def write_factor_info_chart(self, factor_info, df_factor):        
        for k, v in factor_info.iteritems():
            date_list = df_factor['YYYYMM'].tolist()
            iv_ts = df_factor[k].tolist()
            dv_ts = df_factor['DV'].tolist()
            v['iv_ts'] = json.dumps(iv_ts)
            v['dv_ts'] = json.dumps(dv_ts)
            v['date'] = json.dumps(date_list) 

        env = Environment(loader=PackageLoader('wb_engine', 'report/templates'))
        path = os.getcwd() + "\\wb_engine\\report\\"        
        template = env.get_template("factor_info_chart.html")
        temp = template.render(factor_info=factor_info)

        with open(path + "report_factor_info_chart.html", "wb") as fh:
            fh.write(temp)

    def write_iv_ts(self, code, df_iv, iv_info_dict, iv_code):
        
        date_list = df_iv['YYYYMM'].tolist()
        
        iv_ts_list = df_iv[code].tolist()
        iv_thres_list = []
        for i in range(len(iv_ts_list)):
            iv_ts_list[i] = round(iv_ts_list[i], 2)
            iv_thres_list.append(iv_info_dict[code]['thres'])

        dv_ts_list = df_iv['DV'].tolist()
        for i in range(len(dv_ts_list)):
            dv_ts_list[i] = round(dv_ts_list[i], 2)

        # 1. 테이블용 데이터도 뽑는다.
        # 2. 위 배열들로 차트용 데이터 일단 뽑고.
        
        # 테이블용 데이터
        data_table = []        
        for i in range(len(date_list)):
            item = {}
            item['date'] = date_list[i]
            item['iv'] = iv_ts_list[i]
            item['dv'] = dv_ts_list[i]
            data_table.append(item)

        iv_ts_list_chart = []
        dv_ts_list_chart = []
        for i in range(len(iv_ts_list)):
            iv_ts_list_chart.append(round(iv_ts_list[i], 2))
            dv_ts_list_chart.append(round(dv_ts_list[i], 2))

        
        env = Environment(loader=PackageLoader('wb_engine', 'report/templates'))
        template = env.get_template("timeseries.html")        
        temp = template.render(data_table=data_table, iv_info=iv_info_dict[code], \
            name=iv_code[code], chart_iv=json.dumps(iv_ts_list_chart), chart_dv=json.dumps(dv_ts_list_chart), \
            chart_yyyymm=json.dumps(date_list), chart_iv_thres=json.dumps(iv_thres_list))

        path = os.getcwd() + "\\wb_engine\\report\\sub\\"
        with open(path + "iv_%s.html"%(code), "wb") as fh:
            fh.write(temp)


    def write_factor_ts(self, code, df_iv, iv_info_dict, iv_code):
        
        date_list = df_iv['YYYYMM'].tolist()
        iv_ts_list = df_iv[code].tolist()
        dv_ts_list = df_iv['DV'].tolist()

        iv_thres_list = []
        for i in range(len(iv_ts_list)):
            iv_ts_list[i] = round(iv_ts_list[i], 2)
            iv_thres_list.append(iv_info_dict[code]['thres'])

        # 1. 테이블용 데이터도 뽑는다.
        # 2. 위 배열들로 차트용 데이터 일단 뽑고.
        
        # 테이블용 데이터
        data_table = []
        for i in range(len(date_list)):
            item = {}
            item['date'] = date_list[i]
            item['iv'] = iv_ts_list[i]
            item['dv'] = dv_ts_list[i]
            data_table.append(item)

        iv_ts_list_chart = []
        dv_ts_list_chart = []
        for i in range(len(iv_ts_list)):
            iv_ts_list_chart.append(round(iv_ts_list[i], 2))
            dv_ts_list_chart.append(round(dv_ts_list[i], 2))

        
        env = Environment(loader=PackageLoader('wb_engine', 'report/templates'))
        template = env.get_template("timeseries.html")        
        temp = template.render(data_table=data_table, iv_info=iv_info_dict[code], \
            name=code, chart_iv=json.dumps(iv_ts_list_chart), chart_dv=json.dumps(dv_ts_list_chart), \
            chart_yyyymm=json.dumps(date_list), chart_iv_thres=json.dumps(iv_thres_list))

        path = os.getcwd() + "\\wb_engine\\report\\sub\\"
        with open(path + "factor_%s.html"%(code), "wb") as fh:
            fh.write(temp)