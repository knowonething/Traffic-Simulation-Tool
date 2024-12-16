from scapy import all
from util.ParseConfig import Config
from util import sqlite_util

import time
import threading
import os
import json
import base64

class Recorder:
    def __init__(self, config_path:str, sqlite_db_path: str, task_id: str):
        self.config = Config(config_path)
        self.counter = {}
        self.threads = []
        self.sqlite_db_path = sqlite_db_path
        self.task_id = task_id
        self.primary_id = sqlite_util.get_task_primary_id(sqlite_db_path, task_id)[0][0]
        self.prepare()

    def prepare(self):
        config = self.config.get_info()
        iface = None
        if "Interfaces" in config and len(config["Interfaces"]) != 0:
            iface = config["Interfaces"]
        for proto in config["Proto"]:
            thread = threading.Thread(target=thread_function, args=(proto, config["Proto"][proto]["Ports"], self.counter, config["Time"], iface))
            self.threads.append(thread)
            self.counter[proto] = 0

    def start(self):
        for thread in self.threads:
            thread.start()
        print("start monitor......")
        config = self.config.get_info()
        interval = config["Interval"]
        start_time = time.time()
        last_total = 0
        total_time = config["Time"]
        time_for_current_loop = 0 + interval
        time.sleep(start_time + time_for_current_loop - time.time())
        while True:
            total = 0
            monitor_info = {}
            monitor_info["proto"] = {}
            for proto in self.counter:
                total += self.counter[proto]
                monitor_info["proto"][proto] = self.counter[proto]
            monitor_info["total"] = total
            ctime = time.time()
            monitor_info["rate from start"] = total / (ctime - start_time)
            #print(str(monitor_info["rate from start"]) + " pkt/s from start.")
            monitor_info["rate in interval"] = (total-last_total)/interval
            #print(str(monitor_info["rate in interval"]) + " pkt/s in last " + str(interval) + " secconds.")
            # if total != 0:
            #     for proto in self.counter:
            #         print(proto + " : " + str((self.counter[proto] / total) * 100) + "%     " + str(self.counter[proto]))
            # print("total : " + str(total))
            # print()
            args = {
                "related_task_id": self.primary_id,
                "recorder_time": start_time + time_for_current_loop,
                "monitor_info": self.base64_encodestr(json.dumps(monitor_info))
            }
            sqlite_util.add_new_record(self.sqlite_db_path, args)

            last_total = total
            if ctime-start_time > total_time:
                break
            time_for_current_loop = time_for_current_loop + interval
            time.sleep(start_time + time_for_current_loop - time.time())

        args = {
            "related_task_id": self.primary_id,
            "recorder_time": -1,
            "monitor_info": ""
        }
        sqlite_util.add_new_record(self.sqlite_db_path, args)

    def base64_encodestr(self, s: str):
        return bytes.decode(base64.b64encode(str.encode(s)))

    def stop(self):
        args = {
            "related_task_id": self.primary_id,
            "recorder_time": -1,
            "monitor_info": ""
        }
        sqlite_util.add_new_record(self.sqlite_db_path, args)


def thread_function(proto:str, ports:list, counter:dict, timeout:int, iface:list):
    def inner_func(packet):
        counter[proto] += 1
    ports_str = ["tcp port "+str(port) for port in ports]
    afilter = " or ".join(ports_str)
    all.sniff(filter=afilter, prn=inner_func, timeout=timeout, iface=iface)

if __name__ == "__main__":
    recorder = Recorder("/home/yzf/PycharmProjects/traffic-replay/data/config/recorder_config.json")
    recorder.start()

