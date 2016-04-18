#-*- coding: utf-8 -*-
def constant(f):
    def fset(value):
        raise TypeError
    def fget(self):
        return f(self)
    return property(fget, fset)

class Const():
    def __init__(self, fixed):
        self.fixed = fixed

    def isFixed(self):
        return self.fixed

    # 쿼리문 상수
    @constant
    def QR_SELECT_ID_SETUP(self):  # 파라미터 셋업 조건 조회
        return "select * from wbs_id_setup where id_nm = '%s' and cre_seq = %s;"

    @constant
    def QR_SELECT_DV_MAST(self):    # DV 정보 조회
        return "select * from wbs_dv_mast where item_cd = '%s';"

    @constant
    def QR_SELECT_DV(self):  # DV 값 조회
        return "select '', '' union all " \
               "select '', '99999' union all " \
               "select 'trd_dt', 'IDX' union all " \
               "select concat(a.trd_dt, '01') trd_dt, a.amount " \
               "from wbs_ind_var_detail a " \
               "where a.item_cd = '%s'"

    @constant
    def QR_SELECT_ITEM(self):   # 독립변수 아이템 조회
        return "select b.* from " \
               "wbs_id_item a, wbs_ind_var_mast b " \
               "where a.id_nm = '%s' " \
               "and a.cre_seq = '%s' " \
               "and a.item_cd = b.item_cd"

    @constant
    def QR_DELETE_IND_VAR_DETAIL_SET(self):  # 독립변수 값들 삭제
        return """DELETE from wbs_ind_var_detail_set where id_nm = %s"""

    @constant
    def QR_INSERT_IND_VAR_DETAIL_SET(self):  # 독립변수 값들 생성
        return """INSERT INTO wbs_ind_var_detail_set
            (ID_NM, TRD_DT, ITEM_CD, DIFF_AMOUNT, CRISIS_GB, UP_DN, NTS,
            THRESHOLD, VAR_A, VAR_B, VAR_C, VAR_D, ADF_GB)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    @constant
    def QR_DELETE_FACT_INFO_SET(self):    # 팩터 값들 삭제
        query = """DELETE from """ + self.TBL_FACT_INFO
        if not self.isFixed():
            query += """ where id_nm = %s and cre_seq = %s"""

        return query

    @constant
    def QR_INSERT_FACT_INFO_SET(self):    # 팩터 값들 생성
        query = """INSERT INTO """ + self.TBL_FACT_INFO

        if self.isFixed():
            query += """
            (TRD_DT, FACT_NM, AMOUNT, FACT_WT, FACT_NTS,
            VAR_A, VAR_B, VAR_C, VAR_D, CRISIS_GB, UP_DN, ADF_GB, FACT_THRESHOLD )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        else:
            query += """
            (CRE_SEQ, ID_NM, TRD_DT, FACT_NM, AMOUNT, FACT_WT, FACT_NTS,
            VAR_A, VAR_B, VAR_C, VAR_D, CRISIS_GB, UP_DN, ADF_GB, FACT_THRESHOLD )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        return query

    @constant
    def QR_DELETE_IND_WT_SET(self):  # 독립변수 비중 값들 삭제
        query = """DELETE from """ + self.TBL_IND_WT
        if not self.isFixed():
            query += """ where id_nm = %s and cre_seq = %s"""

        return query

    @constant
    def QR_INSERT_IND_WT_SET(self):  # 독립변수 비중 값들 생성

        query = """INSERT INTO """ + self.TBL_IND_WT

        if self.isFixed():
            query += """
            (TRD_DT, FACT_NM, ITEM_CD, ITEM_WT)
            VALUES(%s, %s, %s, %s)"""
        else:
            query += """
            (CRE_SEQ, ID_NM, TRD_DT, FACT_NM, ITEM_CD, ITEM_WT)
            VALUES(%s, %s, %s, %s, %s, %s)"""

        return query

    @constant
    def QR_DELETE_IDX_SET(self):  # 위기지수 삭제
        query = """DELETE from """ + self.TBL_IDX
        if not self.isFixed():
            query += """ where id_nm = %s and cre_seq = %s"""

        return query

    @constant
    def QR_INSERT_IDX_SET(self):  # 위기지수 생성

        query = """INSERT INTO """ + self.TBL_IDX

        if self.isFixed():
            query += """
            (TRD_DT, ITEM_CD, AMOUNT)
            VALUES(%s, %s, %s)"""
        else:
            query += """
            (CRE_SEQ, ID_NM, TRD_DT, ITEM_CD, AMOUNT)
            VALUES(%s, %s, %s, %s, %s)"""

        return query

    # 테이블명 상수
    @constant
    def TBL_IDX(self):
        if self.isFixed():
            return 'WBS_IDX_FIX'
        else:
            return 'WBS_IDX_SET'

    @constant
    def TBL_FACT_INFO(self):
        if self.isFixed():
            return 'WBS_FACT_INFO_FIX'
        else:
            return 'WBS_FACT_INFO_SET'

    @constant
    def TBL_IND_WT(self):
        if self.isFixed():
            return 'WBS_IND_WT_FIX'
        else:
            return 'WBS_IND_WT_SET'
