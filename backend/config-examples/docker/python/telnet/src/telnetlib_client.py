import telnetlib
import sys
import os
import time
import random


def main(host:str, username:str, password:str):
    tn = telnetlib.Telnet(host)
    getinfo(tn)
    getinfo(tn, username)
    getinfo(tn, password)
    num = 0
    while num < 10:
        user_operation_interval()
        getinfo(tn, "pwd")
        user_operation_interval()
        getinfo(tn, "ls")
        user_operation_interval()
        getinfo(tn, "mkdir abc")
        user_operation_interval()
        getinfo(tn, "ls")
        user_operation_interval()
        getinfo(tn, "rm -rf abc")
        user_operation_interval()
        getinfo(tn, "ls")
        user_operation_interval()
        getinfo(tn, "../..")
        user_operation_interval()
        getinfo(tn, "ls")
        user_operation_interval()
        getinfo(tn, "cat cmd.sh")
        user_operation_interval()
        getinfo(tn, "cd /home/user")
        num += 1
    tn.close()


def getinfo(tn, cmd: str = None):
    if cmd is not None:
        tn.write(cmd.encode('ascii') + b"\n")
    while len(tn.read_eager()) != 0:
        tn.read_eager()

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

