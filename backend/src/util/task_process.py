from Generate.GenerationControl import GenerationControl
from Replay.ReplayControl import ReplayControl
from util.Recorder import Recorder
from util import sqlite_util

import os
import time
import sqlite3
import multiprocessing
import threading
import base64
import json
import signal
import sys

class task_process(multiprocessing.Process):
    def __init__(self, work_content: dict):
        multiprocessing.Process.__init__(self)
        self.work_content = work_content
        self.request_handle = {
            "generate": self.do_generate,
            "simulate": self.do_simulate,
            "monitor": self.do_monitor,
        }
        self.config_file_base_dir = work_content["config_file_base_dir"]
        self.sqlite_db_path = work_content["sqlite_db_path"]
        self.task_id = work_content["ID"]
        self.control_obj = None

    def run(self):
        signal.signal(signal.SIGTERM, self.signal_handle)
        request = self.work_content["request"]
        if request[0] not in self.request_handle:
            return
        self.request_handle[request[0]]()
        info = {
            "summary": "this task stopped normally.",
            "stop time": time.time(),
        }
        sqlite_util.update_task_status_stop(self.sqlite_db_path, self.task_id, info)

    def do_generate(self):
        request = self.work_content["request"]
        request_args = json.loads(self.base64_decodestr(request[1]))
        print(request_args)
        print(request)
        task_config_file_path = request_args["task_config_file_name"]
        real_path = self.translate_file_path(task_config_file_path)
        ctl = ReplayControl(real_path)
        self.control_obj = ctl
        ctl.start(10)
        ctl.wait()

    def do_simulate(self):
        request = self.work_content["request"]
        request_args = json.loads(self.base64_decodestr(request[1]))
        task_config_file_path = request_args["task_config_file_name"]
        real_path = self.translate_file_path(task_config_file_path)
        ctl = GenerationControl(real_path, 20)
        self.control_obj = ctl
        ctl.start()
        ctl.wait()
        ctl.stop()
        ctl.clear()

    def do_monitor(self):
        request = self.work_content["request"]
        request_args = json.loads(self.base64_decodestr(request[1]))
        task_config_file_path = request_args["task_config_file_name"]
        real_path = self.translate_file_path(task_config_file_path)
        recorder = Recorder(real_path, self.sqlite_db_path, self.task_id)
        self.control_obj = recorder
        recorder.start()

    def base64_encodestr(self, s: str):
        return bytes.decode(base64.b64encode(str.encode(s)))

    def base64_decodestr(self, s: str):
        return bytes.decode(base64.b64decode(str.encode(s)))

    def translate_file_path(self, path: str):
        real_name = sqlite_util.query_file_real_name(self.sqlite_db_path, path.strip())[0][0]
        return os.path.join(self.config_file_base_dir, path)

    def signal_handle(self, signum, frame):
        self.control_obj.stop()
        sys.exit(0)
