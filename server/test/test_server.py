import mysql.connector

def init_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='n3u3da!',
        database='bygDB'
    )

# JUST FOR TEST PURPOSES - testing the connection
def test_show_all_table():
    db = init_db()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    result = cursor.fetchall()
    for row in result:
        print(row)  
        
    cursor.close()
    db.close()

def test_add_sample_user():
    db = init_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO accounts (balance) VALUES (0.00);")
    cursor.execute("INSERT INTO users (username, name, birth_date, email, account_id) VALUES ('Baibhav B.', 'barwalb', '2001-10-20', 'barwal0011@gmail.com;', LAST_INSERT_ID());")
    db.commit()
    print("New user added successfully!")   
    
    
if __name__ == "__main__":
    #test_show_all_table()
    test_add_sample_user()