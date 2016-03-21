# -*- coding: utf-8 -*-
import sys, locale, wb_engine.read, datetime, os
from wb_engine.utility import DateUtility
from wb_engine.io import IO
from wb_engine.preprocessing import PreProcessing
from wb_engine.engine import WbEngine
from wb_engine.report_excel.report_generator import ExcelReportGenerator
from wb_engine.io_template import IoTemplate

reload(sys)
sys.setdefaultencoding('utf-8')
#print sys.getdefaultencoding()
#print locale.getpreferredencoding()

print '*************************************************'
print 'Shipping indstry Early Warning System Version 1.0'
print '*************************************************'
print ''
print 'Please enter input parameters below'


nts = input('NTS(0 ~ 1):')
t0 = str(input('t0(Time_Start:YYYYMM):')) + '01'
t1 = str(input('t1(Time_End:YYYYMM):')) + '01'
t2 = str(input('t2(Learning_Time:YYYYMM):')) + '01'
pca_thres = float(input('pca threshold(0 ~ 1):'))
intv = input('lag(MM):')
lag_cut = input('lag_cut(MM):')
scaling = str(input('scaling(yes:1, no:0):'))
hp_filter = input('hp_filter(0 ~ 100)%:')


# INPUT SETTING ##################################
params = {}
params['t0'] = datetime.date(2004, 1, 1)         # 데이터 초기 시점
params['t1'] = datetime.date(2012, 3, 1)         # 데이터 로딩 마지막 시점
params['t2'] = datetime.date(2015, 3, 1)         # 데이터 러닝 마지막 시점
params['nts_thres'] = 0.5                        # NTS 필터 값
params['hp_filter'] = 10                         # HP필터 값
params['pca_thres'] = 0.9                        # PCA 필터 값
params['dv_dir'] = 'up'                          # 종속변수 위기 방향
params['intv'] = 6                               # 위기발생유효기간
params['lag_cut'] = 6                             # 위기발생 인식기간 제한
params['thres_cut'] = 0.2                        # 상위 20% 컷
params['dv_thres'] = 7                           # 종속변수 임계치
params['scaling'] = '1'                          # 데이터 스케일링 유무
##################################################


# 입력받은 인풋으로 한번더 #######################

params['nts_thres'] = nts
params['t0'] = datetime.datetime.strptime(str(t0), '%Y%m%d').date()
params['t1'] = datetime.datetime.strptime(str(t1), '%Y%m%d').date()
params['t2'] = datetime.datetime.strptime(str(t2), '%Y%m%d').date()
params['pca_thres'] = pca_thres
params['intv'] = int(intv)
params['lag_cut'] = int(lag_cut)
params['scaling'] = scaling
params['hp_filter'] = hp_filter


##################################################

engine = WbEngine()
result = engine.run(params)

# html
report_html = IoTemplate()
report_html.make_report(result)

# excel
report_module = ExcelReportGenerator()
report_module.make_report(result)

