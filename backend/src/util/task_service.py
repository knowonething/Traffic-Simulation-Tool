from Generate.GenerationControl import GenerationControl
from Replay.ReplayControl import ReplayControl
from util.Recorder import Recorder
from util import sqlite_util
from util.task_process import task_process

import time
import sqlite3
import multiprocessing
import threading
import base64
import heapq
import json

class TaskService:
    def __init__(self, sqlite_db_path: str, config_file_base_dir: str):
        self.sqlite_db_path = sqlite_db_path
        self.config_file_base_dir = config_file_base_dir

        self.tasks = {}  # 任务ID和进程实例的映射
        self.tasks_lock = threading.Lock()

        self.tasks_to_start = []  # 将要执行的任务，用优先队列排序启动时间
        self.tasks_to_start_map = {}  # 从ID到优先队列中节点的映射，节点为元组，分别是 启动时间戳、id、任务是否已经停止
        self.tasks_to_start_lock = threading.Lock()

        self.request_handles = {
            "stop task": self.stop_task,
            "delete task": self.delete_task,
            "generate": self.create_task_with_start_time,
            "simulate": self.create_task_with_start_time,
            "monitor": self.create_task_with_start_time,
        }

        self.tasks_need_ID = {"generate", "simulate", "monitor"}
        self.tasks_need_start_time = {"generate", "simulate", "monitor"}

    def init(self):
        # 辅助线程，用于启动创建的进程
        thread = threading.Thread(target=self.check_time_to_start_task)
        thread.start()

    def run_server(self):
        self.init()

        print("开始循环监听指令。")
        while True:
            time.sleep(0.5)
            request = self.get_next_request()
            if request is None:
                continue
            if request[0] not in self.request_handles:
                print("instruction not support: ", request[0])
                continue
            print("get instruction: ", request[0])
            thread = threading.Thread(target=self.request_handles[request[0]], args=(request,))
            thread.start()

    def get_next_request(self):
        result = sqlite_util.select_first_request_and_delete_it(self.sqlite_db_path)
        if len(result) == 0:
            return None
        else:
            return result[0][1:]

    def get_new_task_ID(self, usage: str):
        task_ID = self.base64_encodestr(str(time.time()) + ":" + usage)
        return task_ID

    def create_task_with_start_time(self, request: tuple):
        # 先在上下文保存信息，然后再在表中保存信息，防止网页端命令我们修改上下文中还未保存的信息，会出现错误
        # 首先创建好进程
        task_id = self.get_new_task_ID(request[0])
        work_content = {
            "request": request,  # 具体的请求信息在哪里都可能需要
            "sqlite_db_path": self.sqlite_db_path,  # 可能需要使用数据库
            "config_file_base_dir": self.config_file_base_dir,
            "ID": task_id,  # 这一类任务需要ID信息
        }
        task = task_process(work_content)  # 创建后task状态是 created
        created_time = self.extract_created_time(task_id)
        # 然后先提前计算需要的信息，request的第一个是指令，第二个是json参数，已经用base64编码了，第三位是浮点数
        request_args = json.loads(self.base64_decodestr(request[1]))
        start_time = float(request[2])
        # 然后要记录该进程
        # 先在当前进程上下文记录
        self.tasks_lock.acquire()
        self.tasks[task_id] = task
        self.tasks_lock.release()
        self.tasks_to_start_lock.acquire()
        # 第一项用于排序，是启动时间，第二项用于索引，是id，第三项则用于标记该任务是否已经被停止了，0表示没有，非0表示已经停止
        item = (start_time, task_id, 0)
        heapq.heappush(self.tasks_to_start, item)
        self.tasks_to_start_map[task_id] = item
        self.tasks_to_start_lock.release()
        # 再在表中记录
        extra_info = {
            "summary": "该任务已经下发，等待启动。",
        }
        args = {
            "task_id": task_id,  # 任务ID在获取时已经是base64编码得了
            "task_config_file_name": request_args["task_config_file_name"],
            "task_status": "created",  # 任务刚刚创建，由子线程启动并修改该字段
            "task_type": request[0],
            "task_extra_info": self.base64_encodestr(json.dumps(extra_info)),
            "task_creation_time": created_time,
        }
        sqlite_util.add_a_task(self.sqlite_db_path, args)
        print("task created: ", request[0])

    def create_task_without_start_time(self, request: tuple):
        # 首先创建好进程
        work_content = {
            "request": request,  # 具体的请求信息在哪里都可能需要
            "sqlite_db_path": self.sqlite_db_path,  # 可能需要使用数据库
        }
        task = task_process(work_content)  # 直接处于运行状态
        # 然后启动进程
        task.start()  # 直接启动

    def stop_task(self, request: tuple):
        # 先在上下文中修改改动task，然后在表中修改task状态，防止网页端命令我们修改上下文中还没保存的信息
        # 首先准备要用到的信息
        request_args = json.loads(self.base64_decodestr(request[1]))
        task_id = request_args["task_id"]
        # 然后改动task
        # 对于等待启动的任务，不让他启动
        not_start_flag = 0
        self.tasks_to_start_lock.acquire()
        if task_id in self.tasks_to_start_map:
            not_start_flag = 1  # 表示该任务还没有被启动
            self.tasks_to_start_map[task_id][2] = 1  # 第三项非0，表示该任务已经被停止
        self.tasks_to_start_lock.release()
        # 还存活的进程，杀死，已经死亡的进程，不需要处理
        self.tasks_lock.acquire()
        if task_id not in self.tasks:
            task = None
        else:
            task = self.tasks[task_id]
        self.tasks_lock.release()
        if task is None:  # 如果该任务不存在，例如已经被删除了，或者id根本就是错误的，那么直接退出
            return
        if not task.is_alive():  # 可能是进程还未启动，也可能是已经停止
            if not_start_flag == 0:  # 如果该进程是自己停止的，并不是还没有启动
                return
            # 到这里是因为该进程还没有被启动
        else:
            # 该进程存活，已经被启动了
            task.terminate()
        # 到这里，说明是用户亲手停止进程，修改表中的信息
        info = {
            "summary": "该任务由用户手动停止",
            "stopped time": str(time.time())
        }
        sqlite_util.update_task_status_stop(self.sqlite_db_path, task_id, info)

    def delete_task(self, request: tuple):
        # 修改表，不让用户再次看见该任务，以及从上下文中删除信息
        # 首先准备要用到的信息
        request_args = json.loads(self.base64_decodestr(request[1]))
        task_id = request_args["task_id"]
        # 任务一定要先停止，再删除
        status = sqlite_util.get_task_status(self.sqlite_db_path, task_id)[0][0]
        if status != "stopped":
            return
        # 先修改表
        sqlite_util.delete_a_task(self.sqlite_db_path, task_id)
        # 然后删除信息
        self.tasks_lock.acquire()
        if task_id in self.tasks:
            del self.tasks[task_id]
        self.tasks_lock.release()

    def check_time_to_start_task(self):
        while True:
            current_time = time.time()
            self.tasks_to_start_lock.acquire()
            if len(self.tasks_to_start) == 0:
                self.tasks_to_start_lock.release()
                time.sleep(0.5)
                continue
            if self.tasks_to_start[0][0] > current_time:  # 检查优先队列的第一个位置上的启动时间
                start_time = self.tasks_to_start[0][0]
                self.tasks_to_start_lock.release()
                time.sleep(start_time - time.time())
                continue
            else:  # 优先队列的第一个可以启动了
                item = heapq.heappop(self.tasks_to_start)
                del self.tasks_to_start_map[item[1]]
                self.tasks_to_start_lock.release()
                if item[2] != 0:  # 非零表示已经停止，或许是用户要求提前停止的
                    continue
                self.tasks_lock.acquire()
                task = self.tasks[item[1]]
                self.tasks_lock.release()
                task.start()
                sqlite_util.update_task_status_running(self.sqlite_db_path, item[1])

    def base64_encodestr(self, s: str):
        return bytes.decode(base64.b64encode(str.encode(s)))

    def base64_decodestr(self, s: str):
        return bytes.decode(base64.b64decode(str.encode(s)))

    def extract_created_time(self, s: str):
        decode_s = self.base64_decodestr(s)
        return float(decode_s.split(":")[0].strip())

def add_data():
    def base64_decodestr(s: str):
        return bytes.decode(base64.b64decode(str.encode(s)))

    def base64_encodestr(s: str):
        return bytes.decode(base64.b64encode(str.encode(s)))

    db_path = "D:/PycharmProjects/DjangoBackend/mysite/db.sqlite3"
    types = ["generate", "simulate", "monitor"]
    configs = ["/c1", "/c2"]
    statuss = ["created", "running", "stopped"]
    summarys = {
        "created": "任务已经下发，等待启动中。",
        "running": "任务正在运行中。",
        "stopped": "任务已经停止"
    }
    for ttype in types:
        for config in configs:
            for status in statuss:
                current_time = time.time()
                extra_info = {
                    "summary": summarys[status],
                }
                task_id = base64_encodestr(str(time.time()) + ":" + ttype)
                args = {
                    "task_id": task_id,  # 任务ID在获取时已经是base64编码得了
                    "task_config_file_name": config,
                    # 文件路径也一律用base64编码
                    "task_status": status,  # 任务刚刚创建，由子线程启动并修改该字段
                    "task_type": ttype,
                    "task_extra_info": base64_encodestr(json.dumps(extra_info)),
                    "task_creation_time": current_time
                }
                sqlite_util.add_a_task(db_path, args)

    result = sqlite_util.select_all_tasks(db_path)

    return

def add_data2():
    def base64_decodestr(s: str):
        return bytes.decode(base64.b64decode(str.encode(s)))

    def base64_encodestr(s: str):
        return bytes.decode(base64.b64encode(str.encode(s)))

    db_path = "D:/PycharmProjects/DjangoBackend/mysite/db.sqlite3"
    usages = ["generate", "simulate", "monitor"]
    paths = ["/c1", "/c2"]
    summarys = {
        "generate": "该文件用于生成定制流量",
        "simulate": "该文件用于模拟用户行为流量。",
        "monitor": "该文件用于监视流量动态"
    }
    for usage in usages:
        for path in paths:
            current_time = time.time()
            args = {
                "file_usage": usage,
                "file_path": base64_encodestr(path),
                "file_creation_time": current_time,
                "file_description": summarys[usage]
            }
            sqlite_util.add_config_file(db_path, args)

    result = sqlite_util.select_all_fileinfo(db_path)

    return

def add_data3():
    def base64_decodestr(s: str):
        return bytes.decode(base64.b64decode(str.encode(s)))

    def base64_encodestr(s: str):
        return bytes.decode(base64.b64encode(str.encode(s)))

    db_path = "D:/PycharmProjects/DjangoBackend/mysite/db.sqlite3"

    related_task = "MTY0NzEwNjE2NC41MTU0MTA0Om1vbml0b3I="
    ctime = time.time()
    num = 20
    numinfo = [0, 1, 2]
    for i in range(num):
        monitor_info = {"proto": {
            "http": numinfo[0],
            "ftp": numinfo[1],
            "telnet": numinfo[2]
        }}
        args = {
            "related_task_id": 17,
            "recorder_time": ctime,
            "monitor_info": base64_encodestr(json.dumps(monitor_info))
        }
        sqlite_util.add_new_record(db_path, args)
        numinfo[0] += 1
        numinfo[1] += 2
        numinfo[2] += 3
        ctime += 3
    args = {
        "related_task_id": 17,
        "recorder_time": -1,
        "monitor_info": ""
    }
    sqlite_util.add_new_record(db_path, args)
    return

if __name__ == "__main__":
    # add_data()
    # add_data3()
    TS = TaskService("/home/yzf1/PycharmProjects/DjangoBackend/mysite/db.sqlite3", "/home/yzf1/config-files/")
    TS.run_server()
