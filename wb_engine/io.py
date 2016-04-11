# -*- coding: utf-8 -*-
import sys, xlrd, datetime, calendar, os, csv
reload(sys)
sys.setdefaultencoding('utf-8')
from wb_engine.read import Series

class IO():

    def __init__(self): # SERIES 출력
        self.output_path = os.getcwd() + "\\output";
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def print_df(self, filename, df):
        filepath = self.output_path + "\\%s.txt"%(filename)
        f = open(filepath, 'w')
        f.write(df.to_csv())
        f.close()

    def print_series_list_raw(self, series_list, filename):

        series_dict = []
        for series in series_list:
            series_dict.append(series.__dict__)

        filepath = self.output_path + "\\%s.txt"%(filename)
        f = open(filepath, 'w')
        writer = csv.DictWriter(f, series_dict[0].keys())
        writer.writeheader()
        writer.writerows(series_dict)
        f.close()

    def print_nts_info(self, info, filename):        
        filepath = self.output_path + "\\%s.txt"%(filename)
        info_list = []
        for k, v in info.iteritems():
            v['code'] = k
            info_list.append(v)
        with open(filepath, 'wb') as f:
            w = csv.DictWriter(f, info_list[0].keys())
            w.writeheader()
            w.writerows(info_list)

    def print_dict(self, filename, dict):
        filepath = self.output_path + "\\%s.txt"%(filename)
        f = open(filepath, 'w')
        test = {}        
        for k,v in dict.iteritems():
            f.write("%s,%s\n"%(k,v))
        f.close()