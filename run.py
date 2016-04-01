# -*- coding: utf-8 -*-
import sys
import locale
import wb_engine.read
import datetime
import os
import optparse
from wb_engine.utility import DateUtility
from wb_engine.io import IO
from wb_engine.preprocessing import PreProcessing
from wb_engine.engine import WbEngine
from wb_engine.report_excel.report_generator import ExcelReportGenerator
from wb_engine.io_template import IoTemplate

parser = optparse.OptionParser('usage run.py <options>')
parser.add_option(
    '--debug',
    action='store_true',
    dest='debug',
    default=False,
    help='set debug options')

parser.add_option(
    '-d', '--default',
    action='store_true',
    dest='default',
    default=False,
    help='set default options')

parser.add_option(
    '-f', '--fix',
    action='store_true',
    dest='fix',
    default=False,
    help='use fixed conditions')

parser.add_option(
    '-i', '--id',
    dest='userId',
    default='',
    help='set user id')

parser.add_option(
    '-s', '--seq',
    dest='seq',
    default='1',
    help='set sequence')

(options, args) = parser.parse_args()

if options.fix is False and options.userId is '':
    print 'insert fix option or user id, seq options'
    sys.exit()


reload(sys)
sys.setdefaultencoding('utf-8')
# print sys.getdefaultencoding()
# print locale.getpreferredencoding()

print '*************************************************'
print 'Shipping indstry Early Warning System Version 1.2'
print '*************************************************'

# INPUT SETTING ##################################
paramsDefault = {
    'nts_thres': 0.5                        # NTS 필터 값
    , 't0': datetime.date(2004, 2, 1)         # 데이터 초기 시점
    , 't1': datetime.date(2004, 9, 1)         # 데이터 로딩 마지막 시점
    , 't2': datetime.date(2004, 9, 1)         # 데이터 러닝 마지막 시점
    , 'hp_filter': 10                         # HP필터 값
    , 'pca_thres': 0.9                        # PCA 필터 값
    , 'dv_dir': 'up'                          # 종속변수 위기 방향
    , 'intv': 6                               # 위기발생유효기간
    , 'lag_cut': 6                             # 위기발생 인식기간 제한
    , 'thres_cut': 0.2                        # 상위 20% 컷
    , 'dv_thres': 7                           # 종속변수 임계치
    , 'scaling': '1'                          # 데이터 스케일링 유무
}
##################################################

if options.default:
    params = {}
    params['nts_thres'] = paramsDefault['nts_thres']
    params['t0'] = paramsDefault['t0']
    params['t1'] = paramsDefault['t1']
    params['t2'] = paramsDefault['t2']
    params['pca_thres'] = paramsDefault['pca_thres']
    params['intv'] = paramsDefault['intv']
    params['lag_cut'] = paramsDefault['lag_cut']
    params['scaling'] = paramsDefault['scaling']
    params['hp_filter'] = paramsDefault['hp_filter']
    params['dv_dir'] = paramsDefault['dv_dir']
    params['thres_cut'] = paramsDefault['thres_cut']
    params['dv_thres'] = paramsDefault['dv_thres']
else:
    print ''
    print 'Please enter input parameters below'

    # 입력 인풋으로 한번더 #######################
    nts = raw_input('NTS(0 ~ 1):')
    t0 = raw_input('t0(Time_Start:YYYYMM):')
    t1 = raw_input('t1(Time_End:YYYYMM):')
    t2 = raw_input('t2(Learning_Time:YYYYMM):')
    pca_thres = raw_input('pca threshold(0 ~ 1):')
    intv = raw_input('lag(MM):')
    lag_cut = raw_input('lag_cut(MM):')
    scaling = str(raw_input('scaling(yes:1, no:0):'))
    hp_filter = raw_input('hp_filter(0 ~ 100)%:')

    params = {}
    params['nts_thres'] = nts and float(nts) or paramsDefault['nts_thres']
    params['t0'] = t0 and datetime.datetime.strptime(
        str(t0) + '01', '%Y%m%d').date() or paramsDefault['t0']
    params['t1'] = t0 and datetime.datetime.strptime(
        str(t0) + '01', '%Y%m%d').date() or paramsDefault['t1']
    params['t2'] = t0 and datetime.datetime.strptime(
        str(t0) + '01', '%Y%m%d').date() or paramsDefault['t2']
    params['pca_thres'] = pca_thres and float(
        pca_thres) or paramsDefault['pca_thres']
    params['intv'] = intv and int(intv) or paramsDefault['intv']
    params['lag_cut'] = lag_cut and int(lag_cut) or paramsDefault['lag_cut']
    params['scaling'] = scaling or paramsDefault['scaling']
    params['hp_filter'] = hp_filter or paramsDefault['hp_filter']
    params['dv_dir'] = paramsDefault['dv_dir']
    params['thres_cut'] = paramsDefault['thres_cut']
    params['dv_thres'] = paramsDefault['dv_thres']

# for x in params:
#     print "%s : %s" %(x, params[x])

##################################################

engine = WbEngine()
result = engine.run(params, options)

# html
report_html = IoTemplate()
report_html.make_report(result)

# excel
report_module = ExcelReportGenerator()
report_module.make_report(result)
