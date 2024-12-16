import paramiko
import sys
import os
import time
import random


def main(host:str, port:int, username:str, password:str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    client.connect(host, port=port, username=username, password=password)
    num = 0
    while num < 10:
        user_operation_interval()
        client.exec_command("pwd")
        user_operation_interval()
        client.exec_command("ls")
        user_operation_interval()
        client.exec_command("whoami")
        user_operation_interval()
        client.exec_command("whoami")
        num += 1
    client.close()


def user_operation_interval():
    return random.random()*1.0


def user_connection_interval():
    return random.random()*2.0

if __name__ == "__main__":
    current_env = os.environ
    host = current_env.get("SERVER_HOST")
    username = current_env.get("USERNAME")
    password = current_env.get("PASSWORD")
    port = current_env.get("SERVER_PORT")
    if port is None:
        port = 22
    if None in [host, username, password]:
        sys.exit(-1)
    print([host, port, username, password])
    while True:
        main(host, port, username, password)
        time.sleep(user_connection_interval())

