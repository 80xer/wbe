#-*- coding:cp949 -*-
import sys, MySQLdb, datetime
from wb_engine.utility import DateUtility
from wb_engine.utility import Utility
from wb_engine.read import Series

reload(sys)
sys.setdefaultencoding('utf-8')

class dbHelper():
    def __init__(self):
        self.__wbsDbConfig = {
            'user': 'wbsuser',
            'password': 'wbsuser2016',
            'host': '11.4.3.229',
            'database': 'wbs',
            'raise_on_warnings': True
        }

    def getConn(self):
        config = self.__wbsDbConfig
        self.conn = MySQLdb.connect(host=config["host"], port=3306, user=config["user"], passwd=config["password"], db=config["database"], charset ='utf8')
        return self.conn

    def exeData(self, query):
        conn = self.getConn()
        cur = conn.cursor()

        cur.execute(query)
        results = cur.fetchall()

        conn.close()
        return results

    def executeMany(self, query, data):
        conn = self.getConn()
        cur = conn.cursor()

        try:
           cur.executemany(query, data)
           conn.commit()
        except Exception as inst:
            print type(inst)
            print inst.args
            conn.rollback()

        conn.close()

class queries():
    def __init__(self):
        self.utility = Utility()

    def getSetup(self, id, seq):

        # 변수별 컬럼 값
        ID_NM = 0
        SEQ = 1
        START_DT = 2
        END_DT = 3
        LEARN_DT = 4
        NTS = 5
        FILTER = 6
        PCA = 7
        LAG = 8
        SCALING = 9
        DV = 10
        LAG_CUT = 11
        SHIFT = 12

        # DV
        DIR = 3
        THRESHOLD = 2

        db = dbHelper()
        dataTuples = db.exeData("select * from wbs_id_setup where id_nm = '" + id + "' and cre_seq = " + seq + ";")
        dbData = dataTuples[0]

        dataTuples = db.exeData("select * from wbs_dv_mast where item_cd = '" + dbData[DV] + "';")
        dbDataDV = dataTuples[0]

        result = {}
        result['id_nm'] = dbData[ID_NM]
        result['seq'] = dbData[SEQ]
        result['nts_thres'] = dbData[NTS]
        result['t0'] = datetime.datetime.strptime(str(dbData[START_DT]) + '01', '%Y%m%d').date()
        result['t1'] = datetime.datetime.strptime(str(dbData[END_DT]) + '01', '%Y%m%d').date()
        result['t2'] = datetime.datetime.strptime(str(dbData[LEARN_DT]) + '01', '%Y%m%d').date()
        result['pca_thres'] = dbData[PCA]
        result['intv'] = int(dbData[LAG])
        result['lag_cut'] = int(dbData[LAG_CUT])
        result['scaling'] = dbData[SCALING]
        result['hp_filter'] = dbData[FILTER]
        result['dv_dir'] = dbDataDV[DIR]
        result['thres_cut'] = 0.2  # .2 고정
        result['dv_thres'] = dbDataDV[THRESHOLD]
        result['shift'] = dbData[SHIFT]
        return result

    def getDv(self):
        db = dbHelper()
        result = []
        dataTuples = db.exeData("select '', '' union all select '', '99999' union all select 'trd_dt', 'IDX' union all select concat(a.trd_dt, '01') trd_dt, a.amount from wbs_ind_var_detail a where a.item_cd = 'dv'")
        dbData = self.extract_from_list(dataTuples)
        result.extend(dbData)
        return result

    def getItems(self, id, seq):
        db = dbHelper()
        result = db.exeData("select b.* from wbs_id_item a, wbs_ind_var_mast b where a.id_nm = '" + id + "' and a.cre_seq = '" + seq + "' and a.item_cd = b.item_cd")

        itemCdSelect = []
        itemNmSelect = []
        pathSelect = []
        dataSelect = []
        cnt = 0

        itemCdSelect.append("select '', ")
        itemNmSelect.append("select '', ")
        pathSelect.append("select 'TRD_DT', ")
        dataSelect.append("select concat(a.trd_dt,'01'), ")

        for item in result:
            itemCdSelect.append("MAX(iF(a.item_cd = '" + item[0] + "', a.item_cd, null)) 'I'")
            itemNmSelect.append("MAX(iF(a.item_cd = '" + item[0] + "', concat(a.item_nm, '_', a.unit), null)) ")
            pathSelect.append("MAX(iF(a.item_cd = '" + item[0] + "', a.path, null)) ")
            dataSelect.append("MAX(iF(a.item_cd = '" + item[0] + "', a.amount, null)) ")
            if cnt < len(result) - 1:
                itemCdSelect.append(', ')
                itemNmSelect.append(', ')
                pathSelect.append(', ')
                dataSelect.append(', ')
            cnt = cnt + 1

        itemCdSelect.append("from wbs_ind_var_mast a, wbs_id_item b where b.id_nm = '" + id + "' and b.cre_seq = '" + seq + "' and a.item_cd = b.item_cd")
        itemNmSelect.append("from wbs_ind_var_mast a, wbs_id_item b where b.id_nm = '" + id + "' and b.cre_seq = '" + seq + "' and a.item_cd = b.item_cd")
        pathSelect.append("from wbs_ind_var_mast a, wbs_id_item b where b.id_nm = '" + id + "' and b.cre_seq = '" + seq + "' and a.item_cd = b.item_cd")
        dataSelect.append("from wbs_ind_var_detail a, wbs_id_item b where b.id_nm = '" + id + "' and b.cre_seq = '" + seq + "' and a.item_cd = b.item_cd group by a.trd_dt")

        allSelect = []
        allSelect.append(''.join(itemCdSelect))
        allSelect.append(" union all ")
        allSelect.append(''.join(itemNmSelect))
        allSelect.append(" union all ")
        allSelect.append(''.join(pathSelect))
        allSelect.append(" union all ")
        allSelect.append(''.join(dataSelect))

        result = []
        dataTuples = db.exeData(''.join(allSelect))
        dbData = self.extract_from_list(dataTuples)
        result.extend(dbData)
        return result

    def extract_from_list(self, data):
        series_result = []
        date_result = []
        du = DateUtility()
        date_col = 0
        id_row = 0
        nm_row = 1
        unit_row = 2
        start_col = 1
        start_row = 3
        date_values = du.getCol_values(data, date_col, start_row, len(data))

        for i in range(len(date_values)):
            date_str = str(int(date_values[i]))
            date_result.append(datetime.datetime.strptime(date_str, '%Y%m%d').date())
            pass

        col_cnt = len(data[id_row])
        io_type = 'I'
        for i in range(col_cnt)[start_col:]:
            name = data[nm_row][i]
            code = self.utility.convert_code(data[id_row][i])
            unit = data[unit_row][i]
            series = Series()
            series.io_type = io_type
            series.code = code
            series.name = name
            series.group = unit
            series.value = du.getCol_values(data, i, start_row, len(data))
            series.date = date_result
            series.data_cleansing(self.t0, self.t1)
            series.set_freq()

            if series.date[0] <= self.t0 and series.date[-1] >= self.t1:
                series_result.append(series)

        return series_result

class outputToDB:

    def __init__(self, params):
        self.params = params

    def insert_report(self, data):
        self.insert_iv(data)
        self.insert_factor(data)
        self.insert_factor_weight(data)

    def insert_iv(self, data):
        db = dbHelper()
        iv_sh = data['df_iv_sh']
        iv_sh_digit = data['df_iv_sh_digit']
        iv_info = data['iv_info_dict']

        insertData = []
        elem = ()

        for col in iv_sh.columns:
            if col != 'YYYYMM' and col != 'DATE' and col != 'DV':
                for j in range(len(iv_sh[col])):
                    elem = ()
                    if datetime.datetime.strptime(
                        iv_sh['YYYYMM'][j] + '01', '%Y%m%d'
                    ).date() == self.params['t1']:
                        elem = (str(self.params['id_nm']),
                               str(iv_sh['YYYYMM'][j]),
                               str(col),
                               iv_sh[col][j],
                               int(iv_sh_digit[col][j]),
                               iv_info[col]['dir'],
                               iv_info[col]['nts'],
                               iv_info[col]['thres'],
                               iv_info[col]['a'],
                               iv_info[col]['b'],
                               iv_info[col]['c'],
                               iv_info[col]['d'],
                               iv_info[col]['adf_test'],
                               )
                    else:
                        elem = (str(self.params['id_nm']),
                               str(iv_sh['YYYYMM'][j]),
                               str(col),
                               iv_sh[col][j],
                               int(iv_sh_digit[col][j]),
                               None,
                               None,
                               None,
                               None,
                               None,
                               None,
                               None,
                               None,
                               )

                    insertData.append(elem)

        insertStr = """INSERT INTO wbs_ind_var_detail_set
            (ID_NM, TRD_DT, ITEM_CD, DIFF_AMOUNT, CRISIS_GB, UP_DN, NTS,
            THRESHOLD, VAR_A, VAR_B, VAR_C, VAR_D, ADF_GB)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        conn = db.getConn()
        cur = conn.cursor()

        try:
            cur.execute(
                """DELETE from wbs_ind_var_detail_set where id_nm = %s""",
                self.params['id_nm'])
            cur.executemany(insertStr, insertData)
            conn.commit()
        except Exception as inst:
            print type(inst)
            print inst.args
            conn.rollback()

        conn.close()

    def insert_factor(self, data):
        db = dbHelper()
        iv_sh = data['df_factor_yyyymm']
        iv_info = data['factor_info_dict']
        fw = data['factor_weight']
        weight = fw['weight']
        fracs = fw['fracs']

        insertData = []
        elem = ()

        code_ordered = []
        code_ordered.append('YYYYMM')
        for c in iv_sh.columns:
            if c != 'DV' and c != 'YYYYMM':
                code_ordered.append(c)
        code_ordered.append('DV')

        for col in code_ordered:
            if col != 'YYYYMM' and col != 'DATE' and col != 'DV':
                num = col.replace('FAC', '')
                for j in range(len(iv_sh[col])):
                    if datetime.datetime.strptime(
                        iv_sh['YYYYMM'][j] + '01', '%Y%m%d'
                    ).date() == self.params['t1']:
                        elem = (str(self.params['seq']),
                                str(self.params['id_nm']),
                                str(iv_sh['YYYYMM'][j]),
                                str(col),
                                iv_sh[col][j],
                                fracs[int(num)],
                                iv_info[col]['nts'],
                                iv_info[col]['a'],
                                iv_info[col]['b'],
                                iv_info[col]['c'],
                                iv_info[col]['d'],
                                None,
                                iv_info[col]['dir'],
                                None,   #iv_info[col]['adf_test'],
                                iv_info[col]['thres'],
                               )
                    else:
                        elem = (str(self.params['seq']),
                                str(self.params['id_nm']),
                                str(iv_sh['YYYYMM'][j]),
                                str(col),
                                iv_sh[col][j],
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                               )

                    insertData.append(elem)

        insertStr = """INSERT INTO wbs_fact_info_set
            (CRE_SEQ, ID_NM, TRD_DT, FACT_NM, AMOUNT, FACT_WT, FACT_NTS,
            VAR_A, VAR_B, VAR_C, VAR_D, CRISIS_GB, UP_DN, ADF_GB, FACT_THRESHOLD )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        conn = db.getConn()
        cur = conn.cursor()

        try:
            cur.execute(
                """DELETE from wbs_fact_info_set where id_nm = %s and cre_seq = %s""",
                (self.params['id_nm'], self.params['seq']))
            cur.executemany(insertStr, insertData)
            conn.commit()
        except Exception as inst:
            print type(inst)
            print inst.args
            conn.rollback()

        conn.close()

    def insert_factor_weight(self, data):
        db = dbHelper()
        fw = data['factor_weight']
        iv_list = fw['col_list']
        weight = fw['weight']

        insertData = []
        elem = ()

        for i in range(len(weight)):
            for j in range(len(iv_list)):
                # print self.params['seq']
                # print self.params['id_nm']
                # print self.params['t1']
                # print 'FAC%s' %i
                # print iv_list[i]
                # print weight[i][j]

                elem = (str(self.params['seq']),
                        str(self.params['id_nm']),
                        str(self.params['t1'].strftime('%Y%d')),
                        'FAC%s' %i,
                        iv_list[j],
                        weight[i][j]
                       )

                insertData.append(elem)


        insertStr = """INSERT INTO wbs_ind_wt_set
            (CRE_SEQ, ID_NM, TRD_DT, FACT_NM, ITEM_CD, ITEM_WT)
            VALUES(%s, %s, %s, %s, %s, %s)"""

        conn = db.getConn()
        cur = conn.cursor()

        try:
            cur.execute(
                """DELETE from wbs_ind_wt_set where id_nm = %s and cre_seq = %s""",
                (self.params['id_nm'], self.params['seq']))
            cur.executemany(insertStr, insertData)
            conn.commit()
        except Exception as inst:
            print type(inst)
            print inst.args
            conn.rollback()

        conn.close()