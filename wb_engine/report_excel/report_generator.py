# -*- coding: utf-8 -*-
import sys, xlrd, datetime, calendar, os, csv, xlsxwriter
reload(sys)
sys.setdefaultencoding('utf-8')

class ExcelReportGenerator:

    def get_report_path(self):
        path = os.getcwd()
        return path + "\\output\\report_%s.xlsx"%(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))

    def create_excel_file(self, path):
        self._wb = xlsxwriter.Workbook(path)

    def make_report(self, data):
        path = self.get_report_path()
        self.create_excel_file(path)

        # 시뮬레이션 Overview (투입 독립변수 리스트)
        ws_overview = self._wb.add_worksheet() 
        ws_warning_idx_out = self._wb.add_worksheet()        
        self.make_overview_sheet(ws_overview, data)
        
        # independent variables which are proccessed into montly timeseries.
        ws_raw_iv = self._wb.add_worksheet()
        self.make_raw_iv_sheet(ws_raw_iv, self._wb, data)

        # independent variables proccessed into same format(time interval)
        ws_sh_iv = self._wb.add_worksheet()
        self.make_raw_iv_sh(ws_sh_iv, self._wb, data)

        # from independent variables digit(crisis/non crisis) to a,b,c,d which used calculating nts
        ws_sh_iv_digit = self._wb.add_worksheet()
        self.make_iv_digit(ws_sh_iv_digit, data)

        # information & additional calculated information
        ws_iv_info = self._wb.add_worksheet()
        self.make_iv_info(ws_iv_info, data)

        # information & additional calculated information of factors
        ws_factor_info = self._wb.add_worksheet()
        self.make_factor_info(ws_factor_info, data)

        # factor time series
        ws_factor_ts = self._wb.add_worksheet()
        self.make_factor_ts(ws_factor_ts, self._wb, data)

        # warning idx
        # ws_warning_idx = self._wb.add_worksheet()
        self.make_warning_board_idx(ws_overview, self._wb, data)
        self.make_warning_board_idx_out(ws_warning_idx_out, self._wb, data)


        # factor weight
        ws_factor_weight = self._wb.add_worksheet()
        self.make_factor_weight(ws_factor_weight, data)

        self._wb.close()

    def make_overview_sheet(self, sh, data):
        sh.name = u"시뮬레이션 Overview"
        sh.write(0, 0, 'hp_filter')
        sh.write(0, 1, data['params']['hp_filter'])
        sh.write(1, 0, '변동성커버리지')
        sh.write(1, 1, data['params']['pca_thres'])
        sh.write(2, 0, u'데이터시작점')
        sh.write(2, 1, data['params']['t0'].strftime('%Y/%m/%d'))
        sh.write(3, 0, u'데이터마지막시점')
        sh.write(3, 1, data['params']['t1'].strftime('%Y/%m/%d'))
        sh.write(4, 0, u'종속변수임계치')
        sh.write(4, 1, data['params']['dv_thres'])
        sh.write(5, 0, '종속변수상하한경계')
        sh.write(5, 1, data['params']['thres_cut'])
        sh.write(6, 0, 'NTS기준')
        sh.write(6, 1, data['params']['nts_thres'])
        sh.write(7, 0, 'LAG')
        sh.write(7, 1, data['params']['intv'])
        sh.write(8, 0, 'LAG_CUT')
        sh.write(8, 1, data['params']['lag_cut'])

    def make_raw_iv_sheet(self, sh, wb, data):

        sh.name = u"투입독립변수1"
        iv_raw = data['iv_raw']
        col_idx = 8
        iv_cnt = 0
        chart_list = []
        for iv in iv_raw:
            
            sh.write_string(0, col_idx+1, iv.code)
            sh.write_string(1, col_idx+1, iv.name)
            for j in range(len(iv.date)):
                sh.write(j+2, col_idx, iv.date[j].strftime('%Y-%m'))
                sh.write(j+2, col_idx+1, iv.value[j])

            # 차트 그리자
            chart_list.append(wb.add_chart({'type':'line'}))
            chart_list[-1].add_series({
                    'categories': [sh.name, 2, col_idx, len(iv.date)+1, col_idx],
                    'name': iv.name,
                    'values' : [sh.name, 2, col_idx+1, len(iv.date)+1, col_idx+1],
                })
            #chart1.set_style(10)

            chart_list[-1].set_title({'name': iv.name, 'none':True})
            chart_list[-1].set_x_axis({'name': '날짜'})
            chart_list[-1].set_x_axis({'name': iv.name})            
            
            y_offset = int(iv_cnt * (chart_list[-1].height + 50))
            sh.insert_chart('A2', chart_list[-1], {'x_offset':1, 'y_offset':  y_offset})

            col_idx += 2
            iv_cnt += 1

    def make_raw_iv_sh(self, sh, wb, data):
        sh.name = u"독립변수_가공후"
        iv_sh = data['df_iv_sh']
        iv_info = data['iv_info_dict']
         
        COL_IDX_CONST = 8

        col_idx = COL_IDX_CONST
        iv_cnt = 0
        chart_list = []

        for code in iv_sh.columns:
            thred_col_idx = col_idx + len(iv_sh.columns)

            if code == 'YYYYMM':
                sh.write(1, COL_IDX_CONST, u"날짜")                                
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, col_idx, "%s-%s"%(iv_sh[code][j][0:4], iv_sh[code][j][4:6]))
                col_idx += 1
            elif code == 'DATE':
                pass
            elif code == 'DV':
                sh.write(0, col_idx, code)  
                sh.write(1, col_idx, u'종속변수')  
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, col_idx, iv_sh[code][j])
                    sh.write(j+2, col_idx + len(iv_sh.columns), data['dv_thres'])
                dv_col_idx = col_idx
                col_idx += 1
            else:
                sh.write_string(0, col_idx, code)  
                sh.write_string(1, col_idx, data['iv_code'][code])  
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, col_idx, iv_sh[code][j])                    
                
                # 독립변수 임계치
                sh.write(0, thred_col_idx, code)  
                sh.write(1, thred_col_idx, data['iv_code'][code])  
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, thred_col_idx, iv_info[code]['thres'])                    

                # 열 인덱스
                col_idx += 1
                
        
        col_idx = COL_IDX_CONST 
        for code in iv_sh.columns:        
            if code != 'YYYYMM' and code != 'DV' and code != 'DATE':
                                
                col_idx += 1

                # 차트 그리자
                series_len = len(iv_sh.index)
                iv_name = data['iv_code'][code]
                chart_list.append(wb.add_chart({'type':'line'}))
                chart_list[-1].add_series({
                        'categories': [sh.name, 2, COL_IDX_CONST, series_len+1, COL_IDX_CONST],
                        'name': iv_name,
                        'values' : [sh.name, 2, col_idx, series_len+1, col_idx]
                    })                
                chart_list[-1].add_series({
                        'categories': [sh.name, 2, COL_IDX_CONST, series_len+1, COL_IDX_CONST],
                        'name': '독립변수임계치',
                        'values' : [sh.name, 2, col_idx+len(iv_sh.columns), series_len+1, col_idx+len(iv_sh.columns)]
                    })                
                chart_list[-1].add_series({
                        'categories': [sh.name, 2, COL_IDX_CONST, series_len+1, COL_IDX_CONST],
                        'name': u"종속변수",
                        'values' : [sh.name, 2, dv_col_idx, series_len+1, dv_col_idx],
                        'y2_axis': 1
                    })
                chart_list[-1].add_series({
                        'categories': [sh.name, 2, COL_IDX_CONST, series_len+1, COL_IDX_CONST],
                        'name': u"종속변수임계치",
                        'values' : [sh.name, 2, dv_col_idx+len(iv_sh.columns), series_len+1, dv_col_idx+len(iv_sh.columns)],
                        'y2_axis': 1
                    })
                
                #chart_list[-1].set_style(3)
                title = "%s NTS:%.2f 방향성:%s"%(iv_name, iv_info[code]['nts'], iv_info[code]['dir'])
                chart_list[-1].set_title({'name': title, 'name_font':{'size':9}})
                chart_list[-1].set_x_axis({'name': '날짜'})
                chart_list[-1].set_x_axis({'name': iv_name})
                chart_list[-1].set_legend({'position': 'bottom'})
            
                y_offset = int(iv_cnt * (chart_list[-1].height + 50))
                sh.insert_chart('A2', chart_list[-1], {'x_offset':1, 'y_offset':  y_offset})
                iv_cnt += 1

    def make_iv_info(self, sh, data):
          sh.name = u"독립변수별분석_NTS"
          
          iv_code = data['iv_code']
          iv_info = data['iv_info_dict']

          sh.write(0, 0, u'CODE')
          sh.write(0, 1, u'이름')
          sh.write(0, 2, u'그룹')
          sh.write(0, 3, u'방향성')
          sh.write(0, 4, u'NTS')
          sh.write(0, 5, u'임계치')
          sh.write(0, 6, u'A')
          sh.write(0, 7, u'B')
          sh.write(0, 8, u'C')
          sh.write(0, 9, u'D')
          sh.write(0, 10, u'ADF_TEST')
         
          item_cnt = 1
          for k,v in iv_info.iteritems():
              sh.write_string(item_cnt, 0, v['code'])
              sh.write_string(item_cnt, 1, iv_code[v['code']])
              sh.write_string(item_cnt, 2, v['group'])
              sh.write(item_cnt, 3, v['dir'])
              sh.write(item_cnt, 4, v['nts'])
              sh.write(item_cnt, 5, v['thres'])
              sh.write(item_cnt, 6, v['a'])
              sh.write(item_cnt, 7, v['b'])
              sh.write(item_cnt, 8, v['c'])
              sh.write(item_cnt, 9, v['d'])
              sh.write(item_cnt, 10, v['adf_test'])
              item_cnt += 1

    def make_factor_info(self, sh, data):
          sh.name = u"팩터별분석_NTS"

          iv_code = data['iv_code']
          factor_info = data['factor_info_dict']

          sh.write(0, 0, u'CODE')
          # sh.write(0, 1, u'이름')      # 명칭이 없어서 수정
          # sh.write(0, 2, u'그룹')
          sh.write(0, 1, u'방향성')
          sh.write(0, 2, u'NTS')
          sh.write(0, 3, u'임계치')
          sh.write(0, 4, u'A')
          sh.write(0, 5, u'B')
          sh.write(0, 6, u'C')
          sh.write(0, 7, u'D')
         # sh.write(0, 8, u'adf_test')

          item_cnt = 1
          for k,v in factor_info.iteritems():
              sh.write_string(item_cnt, 0, k)
              #sh.write_string(item_cnt, 1, iv_code[v['code']])  make_iv_info로직과 동일
              #sh.write_string(item_cnt, 2, v['group'])
              sh.write(item_cnt, 1, v['dir'])
              sh.write(item_cnt, 2, v['nts'])
              sh.write(item_cnt, 3, v['thres'])
              sh.write(item_cnt, 4, v['a'])
              sh.write(item_cnt, 5, v['b'])
              sh.write(item_cnt, 6, v['c'])
              sh.write(item_cnt, 7, v['d'])
            #  sh.write(item_cnt, 8, v['adf_test'])
              item_cnt += 1

    #펙터정보 시계열
    def make_factor_ts(self, sh, wb, data):
        
        sh.name = u"팩터정보"
        iv_sh = data['df_factor_yyyymm']
        iv_info = data['factor_info_dict']
         
        COL_IDX_CONST = 8

        col_idx = COL_IDX_CONST
        iv_cnt = 0
        chart_list = []

        col_len = len(iv_sh.columns) + 1

        # 컬럼을 YYYYYMM IV DV 순으로 정력
        code_ordered = []
        code_ordered.append('YYYYMM')
        for c in iv_sh.columns:
            if c != 'DV' and c != 'YYYYMM':
                code_ordered.append(c)
        code_ordered.append('DV')

        for code in code_ordered:

            thred_col_idx = col_idx + col_len

            if code == 'YYYYMM':
                sh.write(1, COL_IDX_CONST, u"날짜")                                
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, col_idx, "%s-%s"%(iv_sh[code][j][0:4], iv_sh[code][j][4:6]))
                col_idx += 1
            elif code == 'DATE':
                pass
            elif code == 'DV':
                sh.write(0, col_idx, code)  
                sh.write(1, col_idx, u'종속변수')  
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, col_idx, iv_sh[code][j])
                    sh.write(j+2, col_idx + col_len, data['dv_thres'])
                dv_col_idx = col_idx
                col_idx += 1
            else:
                sh.write(0, col_idx, code)  
                sh.write(1, col_idx, code)  
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, col_idx, iv_sh[code][j])                    
                
                # 독립변수 임계치
                sh.write(0, thred_col_idx, code)  
                sh.write(1, thred_col_idx, code)  
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, thred_col_idx, iv_info[code]['thres'])                    

                # 열 인덱스
                col_idx += 1
                
        
        col_idx = COL_IDX_CONST 
        for code in iv_sh.columns:        
            if code != 'YYYYMM' and code != 'DV' and code != 'DATE':
                                
                col_idx += 1

                # 차트 그리자
                series_len = len(iv_sh.index)
                iv_name = code
                chart_list.append(wb.add_chart({'type':'line'}))
                chart_list[-1].add_series({
                        'categories': [sh.name, 2, COL_IDX_CONST, series_len+1, COL_IDX_CONST],
                        'name': iv_name,
                        'values' : [sh.name, 2, col_idx, series_len+1, col_idx]
                    })                
                chart_list[-1].add_series({
                        'categories': [sh.name, 2, COL_IDX_CONST, series_len+1, COL_IDX_CONST],
                        'name': '독립변수임계치',
                        'values' : [sh.name, 2, col_idx+col_len, series_len+1, col_idx+col_len]
                    })                
                chart_list[-1].add_series({
                        'categories': [sh.name, 2, COL_IDX_CONST, series_len+1, COL_IDX_CONST],
                        'name': u"종속변수",
                        'values' : [sh.name, 2, dv_col_idx, series_len+1, dv_col_idx],
                        'y2_axis': 1
                    })
                chart_list[-1].add_series({
                        'categories': [sh.name, 2, COL_IDX_CONST, series_len+1, COL_IDX_CONST],
                        'name': u"종속변수임계치",
                        'values' : [sh.name, 2, dv_col_idx+col_len, series_len+1, dv_col_idx+col_len],
                        'y2_axis': 1
                    })
                
                #chart_list[-1].set_style(3)
                title = "%s NTS:%.2f 방향성:%s"%(iv_name, iv_info[code]['nts'], iv_info[code]['dir'])
                chart_list[-1].set_title({'name': title, 'name_font':{'size':9}})
                chart_list[-1].set_x_axis({'name': '날짜'})
                chart_list[-1].set_x_axis({'name': iv_name})
                chart_list[-1].set_legend({'position': 'bottom'})
            
                y_offset = int(iv_cnt * (chart_list[-1].height + 50))
                sh.insert_chart('A2', chart_list[-1], {'x_offset':1, 'y_offset':  y_offset})
                iv_cnt += 1

    def make_iv_digit(self, sh, data):
        sh.name = u"독립변수(위기여부)"
        iv_sh = data['df_iv_sh_digit']
        col_idx = 2
        for code in iv_sh.columns:
            if code == 'YYYYMM':
                sh.write(1, 0, u"날짜")                                
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, 0, "%s-%s"%(iv_sh[code][j][0:4], iv_sh[code][j][4:6]))
            elif code == 'DATE':
                pass
            elif code == 'DV':
                sh.write(0, 1, code)  
                sh.write(1, 1, u'종속변수')  
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, 1, iv_sh[code][j])
            else:
                sh.write(0, col_idx, code)  
                sh.write(1, col_idx, data['iv_code'][code])  
                for j in range(len(iv_sh[code])):
                    sh.write(j+2, col_idx, iv_sh[code][j])
                col_idx += 1

    def make_warning_board_idx(self, sh, wb, data):
        sh.name = u"위기지수"
        iv_sh = data['df_warning_idx']
        col_idx = 3
        for code in iv_sh.columns:
            if code == 'YYYYMM':
                sh.write(0, col_idx, u"날짜")                                
                for j in range(len(iv_sh[code])):
                    sh.write(j+1, col_idx, "%s-%s"%(iv_sh[code][j][0:4], iv_sh[code][j][4:6]))
            elif code == 'DATE':
                pass
            elif code == 'DV':
                #sh.write(0, 1, code)  
                sh.write(0, col_idx+1, u'종속변수')  
                for j in range(len(iv_sh[code])):
                    sh.write(j+1, col_idx+1, iv_sh[code][j])
            elif code == 'IDX':
                #sh.write(0, 2, code)  
                sh.write(0, col_idx+2, u'종합위기지수')  
                for j in range(len(iv_sh[code])):
                    sh.write(j+1, col_idx+2, iv_sh[code][j])                

        # 차트 그리자
        series_len = len(iv_sh.index)
        iv_name = code
        chart = wb.add_chart({'type':'line'})
        chart.add_series({
                'categories': [sh.name, 1, col_idx, series_len+1, col_idx],
                'name': u'종합위기지수',
                'values' : [sh.name, 1, col_idx+2, series_len+1, col_idx+2]
            })                        
        chart.add_series({
                'categories': [sh.name, 1, col_idx, series_len+1, col_idx],
                'name': u"종속변수",
                'values' : [sh.name, 1, col_idx+1, series_len+1, col_idx+1],
                'y2_axis': 1
            })
        
        chart.set_title({'name': u'종합위기지수', 'name_font':{'size':9}})
        chart.set_x_axis({'name': u'날짜'})
        chart.set_x_axis({'name': u'종합위기지수'})
        chart.set_legend({'position': 'bottom'})
        
        sh.insert_chart('H1', chart)

    def make_warning_board_idx_out(self, sh, wb, data):
        sh.name = u"위기지수 Out of sample"
        iv_sh = data['df_warning_idx_out']
        col_idx = 3
        for code in iv_sh.columns:
            if code == 'YYYYMM':
                sh.write(0, col_idx, u"날짜")                                
                for j in range(len(iv_sh[code])):
                    sh.write(j+1, col_idx, "%s-%s"%(iv_sh[code][j][0:4], iv_sh[code][j][4:6]))
            elif code == 'DATE':
                pass
            elif code == 'DV':
                #sh.write(0, 1, code)  
                sh.write(0, col_idx+1, u'종속변수')  
                for j in range(len(iv_sh[code])):
                    sh.write(j+1, col_idx+1, iv_sh[code][j])
            elif code == 'IDX':
                #sh.write(0, 2, code)  
                sh.write(0, col_idx+2, u'종합위기지수')  
                for j in range(len(iv_sh[code])):
                    sh.write(j+1, col_idx+2, iv_sh[code][j])

        # 차트 그리자
        series_len = len(iv_sh.index)
        iv_name = code
        chart = wb.add_chart({'type':'line'})
        chart.add_series({
                'categories': [sh.name, 1, col_idx, series_len+1, col_idx],
                'name': u'종합위기지수',
                'values' : [sh.name, 1, col_idx+2, series_len+1, col_idx+2]
            })                        
        chart.add_series({
                'categories': [sh.name, 1, col_idx, series_len+1, col_idx],
                'name': u"종속변수",
                'values' : [sh.name, 1, col_idx+1, series_len+1, col_idx+1],
                'y2_axis': 1
            })
        
        chart.set_title({'name': u'종합위기지수', 'name_font':{'size':9}})
        chart.set_x_axis({'name': u'날짜'})
        chart.set_x_axis({'name': u'종합위기지수'})
        chart.set_legend({'position': 'bottom'})
        
        sh.insert_chart('H1', chart)

    def make_factor_weight(self, sh, data):
        sh.name = u'팩터비중'
        iv_code = data['iv_code']
        fw = data['factor_weight']
        iv_list = fw['col_list']
        weight = fw['weight']
        fracs = fw['fracs']
        factor_info = data['factor_info_dict']

        for i in range(len(weight)):            
            sh.write(0, i+2, fracs[i])
            sh.write(1, i+2, factor_info['FAC%s'%i]['nts'])
            sh.write(2, i+2, factor_info['FAC%s'%i]['dir'])
            sh.write(3, i+2, 'FAC%s'%i)
            for j in range(len(iv_list)):
                sh.write(4+j, i+2, weight[i][j])

        # 독립변수이름 출력
        for i in range(len(iv_list)):
            sh.write_string(i+4, 0, iv_list[i])
            sh.write_string(i+4, 1, iv_code[iv_list[i]])







