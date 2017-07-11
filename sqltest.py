import pymysql

if __name__ == "__main__":
    db = pymysql.connect("db1.antd.nist.gov", "anj1", "dbwr1te!", "time")
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS TEST")
    sq = """CREATE TABLE TEST (
    FIRST_FIELD CHAR(20) NOT NULL,
    SECOND_FIELD INT,
    THIRD_FIELD INT ) """
    cursor.execute(sq)
    sq = """INSERT INTO TEST (FIRST_FIELD, SECOND_FIELD, THIRD_FIELD) 
    VALUES ("test1", 1, 2)"""
    try:
        cursor.execute(sq)
        db.commit()
    except:
        db.rollback()
        
    sq = """SELECT * FROM TEST WHERE SECOND_FIELD > 0"""
    cursor.execute(sq)
    data = cursor.fetchall()
    print (data)
    db.close()
