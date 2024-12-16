import requests
import sys
import os
import time
import random


def user_operation_interval():
    return random.random()*1.0


def get_index_html(host:str):
    requests.get("http://" + host + "/index.html")


def get_indexs_html(host:str):
    requests.get("http://" + host + "/indexs.html")


def main(host:str):
    if random.random() >= 0.8:
        get_index_html(host)
    else:
        get_indexs_html(host)


if __name__ == "__main__":
    current_env = os.environ
    host = current_env.get("SERVER_HOST")
    if None in [host]:
        sys.exit(-1)
    while True:
        main(host)
        time.sleep(user_operation_interval())
