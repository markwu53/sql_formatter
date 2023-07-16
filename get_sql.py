import pymssql

def run():
    connectionParams = {
        "server": r"SQLPEDW\DBP",
        "user": r"mmi\t162880",
        #"password": "Wy@nd0tDublin",
        #"password": "Y0ngDub1in",
        #"password": "SummerPi@no",
        #"password": "WinterV!0lin",
        #"password": "SpringT0w#r",
        #"password": "Winter$20@3",
        #"password": "Winter$@023",
        #"password": "Dublin$!688",
        "password": "NewYork$06@@",
        #"database": "EDW",
        "database": "PK_Stat_Model",
        "autocommit": True,
    }

    conn = pymssql.connect(**connectionParams)
    cursor = conn.cursor()
    sql_command = """
select --distinct o.type_desc
o.name
, len(m.definition) length
, m.definition
from sys.all_sql_modules m
join sys.objects o on m.object_id = o.object_id
where 1=1
--and o.type_desc = 'SQL_STORED_PROCEDURE'
--and o.type_desc = 'SQL_TABLE_VALUED_FUNCTION'
and o.type_desc = 'SQL_SCALAR_FUNCTION'
--and o.name like '%extract%'
--and o.name = 'SP_PLSP_IM_LOSS_INS_STAT_RISK'
order by length desc
    """
    cursor.execute(sql_command)
    results = cursor.fetchall()
    for name, length, defn in results:
        #if name != "SP_PLSP_IM_LOSS_INS_STAT_RISK": continue
        print(name, length)
        fd = open(f"pk_function/{name}.sql", "w", encoding="utf-8")
        fd.write(defn)
    print("done")

if __name__ == "__main__":
    run()    

