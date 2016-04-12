# -*- coding: utf-8 -*-
import sys, xlrd, datetime, pandas
reload(sys)
sys.setdefaultencoding('utf-8')
from wb_engine.utility import DateUtility
from wb_engine.utility import Utility
from wb_engine.preprocessing import PreProcessing


# Series[] 를 'dataframe'으로 변환해 준다.
def convert_series_list_to_dataframe(series_list):
    df = pandas.DataFrame()
    df['YYYYMM'] = pandas.Series(series_list[0].intp_x_str)
    df['DATE'] = pandas.Series(series_list[0].intp_x)
    for series in series_list:
        df[series.code] = pandas.Series(series.intp_y)

    return df


# Series[] 클래스
class Series():
    """
    date  : 날짜배열
    value : value
    freq  : 빈도(M, W, D)
    """
    def __init__(self, params):
        self.date = []
        self.value = []
        self.params = params
        pass

    def set_freq(self):
        if len(self.date) > 1:
            td = self.date[1] - self.date[0] # 두 날짜 사이의 간격
            if td.days > 25:  # 25일 이상일 경우  monthly
                self.freq = 'M'
            elif td.days > 6: # 6일 이상일 경우   weekly
                self.freq = 'W'
            else:             # 그 외             daily
                self.freq = 'D'

    def set_monthly_data(self):
        du = DateUtility()
        # month_list = du.get_montly_span(datetime.date(2001, 1, 1), datetime.date(2014, 12, 30)) #해당 날짜 사이의 YYYYMM을 반환

        # 새 변수 세팅 (월별데이터로 가공된 변수)
        new_date = []
        new_date_months = []
        new_value = []

        for i in range(len(self.date)):
            if datetime.date(self.date[i].year, self.date[i].month, 1) not in new_date:
                # 새로운 月 추가
                new_date.append(datetime.date(self.date[i].year, self.date[i].month, 1))
                # year*12 + month 추가
                new_date_months.append(du.convert2months(new_date[-1]))
                new_value.append(self.value[i])
            else:
                # 가장 최신 데이터로 갱신한다.
                # 월별로 가장 마지막 데이터를 갖고 오는 것.
                new_value[-1] = self.value[i]

        # 기존 변수들 갱신
        self.date = new_date
        self.date_integer = new_date_months
        self.value = new_value

    # 월별 내삽 후 데이터 채워넣기(monthly span에 데이터 채워 맞춤)
    def set_interpolated_data(self, new_x, new_x_str):

        intp = PreProcessing()
        new_y = intp.get_interpolated_y(self.date_integer, self.value, new_x)
        self.intp_x = new_x         # 정수형 날짜
        self.intp_x_str = new_x_str # YYYYMM
        self.intp_y = new_y         # 내삽 결과

    # 데이터 클렌징 null 인것들 제외
    # 시계열 조정되도록 수정 - 2016.04.01 이동은
    #
    def data_cleansing(self, t0, t1):
        new_date = []
        new_value = []
        origin_date = []
        origin_value = []

        for i in range(len(self.value)):
            if self.value[i] != '' and self.value[i] != None:
                idx = self.date[i]  #해수부 시계열 조정 요청에 따라 마지막 데이터 수취 일자 저장.
                origin_value.append(self.value[i])
                origin_date.append(self.date[i])

        if self.params['shift'] == 'Y':

            # 해수부 시계열 조정 요청
            shift = 4

            du = DateUtility()

            diffmonth = du.diff_month(t1, idx)

            if diffmonth < shift:
                shift = diffmonth

            self.value = self.shiftlist(shift, self.value)

            for i in range(len(self.value)):
                if self.value[i] != '' and self.value[i] != None:
                    new_value.append(self.value[i])
                    new_date.append(self.date[i])

            # self.value = origin_value
            # self.date = origin_date

            # 해수부 시계열 조정 요청
            self.value = new_value
            self.date = new_date

        else:
            self.value = origin_value
            self.date = origin_date

    def shiftlist(self, ntimes, lst):
        if ntimes == 0:
            return lst
        else:
            for index in range(len(lst) - 1, 0, -1):
                lst[index] = lst[index - 1]

            return self.shiftlist(ntimes - 1, lst)
        return self.shiftlist(n, lst)


class ReadModule():

    """ 생성자
    ReadModule은 t0와 t1 사이의 데이터만 읽는다.
    """
    def __init__(self, params):
        self.t0 = params['t0']
        self.t1 = params['t1']
        self.utility = Utility()
        self.params  = params

    # 엑셀파일 읽기
    def read_file(self, path):
        print ''
        print u"%s 파일 읽기 시작"%(path)
        workbook = xlrd.open_workbook(path)
        sheets = workbook.sheets()
        result = []
        for sh in sheets:
            one_sheet_data = self.extract_from_sheet(workbook, sh)
            result.extend(one_sheet_data)
        print u"%s 파일 읽기 완료"%(path)
        return result

    # 시트에서 데이터 추출하기
    def extract_from_sheet(self, book, sh, date_col=0, id_row=2, nm_row=3, unit_row=4, start_col=1, start_row=5):
        series_result = []
        du = DateUtility()
        date_values = sh.col_values(date_col, start_rowx=start_row, end_rowx=sh.nrows) # 날짜 값
        date_type = sh.col_types(date_col, start_rowx=start_row, end_rowx=sh.nrows)    # 날짜 타입

        # io_values = sh.col_values(date_col-1)

        date_result = []
        for i in range(len(date_values)):

            if date_type[i] == 3: # 날짜 형식
                date_tuple = xlrd.xldate_as_tuple(date_values[i], book.datemode)
                date_result.append(datetime.date(date_tuple[0], date_tuple[1], date_tuple[2]))
            elif date_type[i] == 2:
                date_str = str(int(date_values[i]))
                date_result.append(datetime.datetime.strptime(date_str, '%Y%m%d').date())
                pass              # 문자열일 경우 처리해 줘야 할듯

        col_cnt = sh.row_len(id_row)

        for i in range(col_cnt)[start_col:]:
        # for i in range(col_cnt)[start_col:4]:
            io_type = sh.cell(id_row-1, i).value
            name = sh.cell(nm_row, i).value
            code = self.utility.convert_code(sh.cell(id_row, i).value)
            unit = sh.cell(unit_row, i).value
            series = Series(self.params)
            series.io_type = io_type
            series.code = code
            series.name = name
            series.group = unit
            series.value = sh.col_values(i, start_row)
            series.date = date_result
            series.data_cleansing(self.t0, self.t1)
            series.set_freq()

            # Full data 만 sheet list에 등록
            du = DateUtility()


            # Full data 만 sheet list에 등록
            if series.date[0] <= self.t0 and series.date[-1] >= self.t1:
                series_result.append(series)

            # if series.date[0] <= self.t0 and series.date[-1] >= du.subtract_months(self.t1, 4):
            #     series_result.append(series)

        return series_result

    # column 개수 구하기
    def column_len(sheet, index):
        col_values = sheet.col_values(index)
        col_len = len(col_values)
        for _ in takewhile(lambda x: not x, reversed(col_values)):
            col_len -= 1
        return col_len
