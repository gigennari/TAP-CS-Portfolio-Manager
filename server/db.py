import mysql.connector
import subprocess
from datetime import datetime
import os 
import glob


MYSQL_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

DB_HOST ='localhost'
DB_USER ='root'
DB_PASSWORD='n3u3da!'
DB_NAME='bygdb'

def init_db():
    
     return mysql.connector.connect(
        host='localhost',
        user='root',
        password='n3u3da!',
        database='bygDB'
    )
    
    
    # conn =  mysql.connector.connect(
    #     host = DB_HOST,
    #     user = DB_USER,
    #     password = DB_PASSWORD,
    # )
    
    # cursor = conn.cursor()
    # cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    # cursor.close()
    
    # conn = mysql.connector.connect(
    #     host = DB_HOST,
    #     user = DB_USER,
    #     password = DB_PASSWORD,
    #     database = DB_NAME
    # )
    # cursor = conn.cursor()
    # cursor.execute(f"USE {DB_NAME}")
    
    # cursor.execute("SHOW TABLES")
    # tables = cursor.fetchall()
    
    # if not tables:
    #  latest_dump = get_latest_dump()
    #  if latest_dump:
    #     try:
    #          with open(latest_dump, "r") as dump_file:
                 
    #             subprocess.run(
    #                 [MYSQL_PATH, 
    #                 f"-u{DB_USER}", 
    #                 f"-p{DB_PASSWORD}",
    #                 "--binary-mode=1", 
    #                 DB_NAME],
    #                 stdin=dump_file,
    #                 check=True
    #             )
    #     except subprocess.CalledProcessError as e:
    #         print(f"Error importing dump file: {e}")
    #     except FileNotFoundError:
    #         print(f"Dump file not found: {latest_dump}")
    
    # return conn
    
    
def get_latest_dump():
    dump_dir = "./data/dumps"
    dumps = [f for f in os.listdir(dump_dir) if f.endswith('.sql')]
    if not dumps:
        return None
    latest_dump = max(dumps, key=lambda x: os.path.getmtime(os.path.join(dump_dir, x)))
    return os.path.join(dump_dir, latest_dump)
    
    

def dump_db():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dump_file = f"./data/dumps/{timestamp}.sql"
    subprocess.run(
        [
            "mysqldump",
            "-u", "root",
            "n3u3da!",  # or better: read from env var
            "bygDB"
        ],
        stdout=open(dump_file, "w"),
        check=True
    )
    
