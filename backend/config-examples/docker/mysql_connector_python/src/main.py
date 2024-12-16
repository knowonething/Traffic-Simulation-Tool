import mysql.connector
import sys
import os
import time
import random


def main(user:str, password:str, host:str, database:str):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
    my_cursor = cnx.cursor()
    my_cursor.execute("SHOW DATABASES;")
    result = my_cursor.fetchall()
    if ("YZF_DATA",) in result:
        return
    my_cursor.execute("SELECT DATABASE();")
    result = my_cursor.fetchall()
    if ("YZF_DATA",) in result:
        my_cursor.execute("USE " + database + ";")

    user_operation_interval()
    create_table(my_cursor)
    user_operation_interval()
    insert_table(my_cursor)
    user_operation_interval()
    select_data(my_cursor)
    user_operation_interval()
    drop_table(my_cursor)

    my_cursor.close()
    cnx.close()
    return

def insert_table(my_cursor):
    cmd = "INSERT IGNORE INTO atable (first_name, last_name) VALUES ('yzf1', 'yzf1'), ('yzf2', 'yzf2');"
    my_cursor.execute(cmd)
    my_cursor.fetchall()

def select_data(my_cursor):
    cmd = "SELECT * FROM atable;"
    my_cursor.execute(cmd)
    my_cursor.fetchall()

def create_table(my_cursor):
    cmd = "CREATE TABLE IF NOT EXISTS atable (`id` int unsigned AUTO_INCREMENT PRIMARY KEY, `first_name` varchar(20), `last_name` varchar(20)) ENGINE=InnoDB;"
    my_cursor.execute(cmd)
    my_cursor.fetchall()

def drop_table(my_cursor):
    cmd = "DROP TABLE IF EXISTS atable"
    my_cursor.execute(cmd)
    my_cursor.fetchall()

def user_operation_interval():
    return random.random()*0.5

def user_connection_interval():
    return random.random()*2.0

if __name__ == "__main__":
    current_env = os.environ
    user = current_env.get("MYSQL_USER")
    password = current_env.get("MYSQL_PASSWORD")
    host = current_env.get("MYSQL_IP")
    database = current_env.get("MYSQL_DATABASE")
    if None in [user, password, host, database]:
        sys.exit(-1)
    while True:
        main(user, password, host, database)
        time.sleep(user_connection_interval())

