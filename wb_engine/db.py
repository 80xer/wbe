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

class queries():
    def __init__(self, t0, t1):
        self.t0 = t0
        self.t1 = t1
        self.utility = Utility()

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
