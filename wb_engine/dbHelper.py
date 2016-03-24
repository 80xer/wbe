import sys, pymysql

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
        self.conn = pymysql.connect(host=config["host"], port=3306, user=config["user"], passwd=config["password"], db=config["database"], charset ='utf8')
        print(self.conn)
        return self.conn

    def exeData(self, query):
        conn = self.getConn()
        cur = conn.cursor()

        cur.execute(query)

        results = cur.fetchall()

        conn.close()
        return results

class queries():
    def getConditions(self, id, seq):
        db = dbHelper()
        return db.exeData("select * from wbs_id_setup where id_nm = 'ADMIN' and cre_seq = '1'")