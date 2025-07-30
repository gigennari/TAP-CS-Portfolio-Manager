import mysql.connector

def init_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='n3u3da!',
        database='bygDB'
    )
    
