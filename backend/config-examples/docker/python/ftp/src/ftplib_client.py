import ftplib
import sys
import os
import time
import random


def main(host:str, username:str, password:str):
    client = ftplib.FTP(host, username, password)
    client.getwelcome()
    client.set_pasv(False)
    num = 0
    while num < 10:
        user_operation_interval()
        client.pwd()
        user_operation_interval()
        client.nlst()
        user_operation_interval()
        client.dir()
        user_operation_interval()
        client.mkd("abc")
        user_operation_interval()
        client.rmd("abc")
        user_operation_interval()
        client.size("123.txt")
        user_operation_interval()
        client.retrbinary("RETR 123.txt", lambda x: None)
        num += 1
    client.quit()


def user_operation_interval():
    return random.random()*1.0


def user_connection_interval():
    return random.random()*2.0

if __name__ == "__main__":
    current_env = os.environ
    host = current_env.get("SERVER_HOST")
    username = current_env.get("USERNAME")
    password = current_env.get("PASSWORD")
    if None in [host, username, password]:
        sys.exit(-1)
    while True:
        main(host, username, password)
        time.sleep(user_connection_interval())

