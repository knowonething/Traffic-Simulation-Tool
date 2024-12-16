import sqlite3
import json
import base64

# ('traffic_replay_webpage_config_files',),
# ('traffic_replay_webpage_current_tasks',),
# ('traffic_replay_webpage_request_queue',),
# ('traffic_replay_webpage_traffic_recorders',)]

# ----------------------------------------------------------------------------------------------------------------------
# traffic_replay_webpage_request_queue 表，由django后台在表结尾增加新的行，由主进程的主线程读取和删除第一行，没有冲突

# 从 traffic_replay_webpage_request_queue 表中选择第一行的请求，如果有，则顺便删除第一行
def select_first_request_and_delete_it(sqlite_db_path: str):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    cursor = connection.execute("SELECT * FROM traffic_replay_webpage_request_queue limit 0,1")
    result = cursor.fetchall()
    if len(result) != 0:
        id = result[0][0]
        sqlstr = f"DELETE FROM traffic_replay_webpage_request_queue where id = {id}"
        connection.execute(sqlstr)
        connection.commit()
    connection.close()
    return result

# ----------------------------------------------------------------------------------------------------------------------
# traffic_replay_webpage_config_files

def select_all_fileinfo(sqlite_db_path: str):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    cursor = connection.execute("SELECT * FROM traffic_replay_webpage_config_files")
    result = cursor.fetchall()
    connection.close()
    return result

def query_file_real_name(sqlite_db_path: str, filename: str):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    cursor = connection.execute(f"SELECT file_obj FROM traffic_replay_webpage_config_files WHERE file_name = '{filename}'")
    result = cursor.fetchall()
    connection.close()
    return result

# ----------------------------------------------------------------------------------------------------------------------
# traffic_replay_webpage_traffic_recorders 表，由django后台读取表的各个行，由主进程启动的子进程增加、删除行、读取行，没有冲突

def add_new_record(sqlite_db_path: str, args:dict):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    sqlstr = f"INSERT INTO traffic_replay_webpage_traffic_recorders (related_task_id, recorder_time, monitor_info) "\
             "VALUES ({related_task_id}, {recorder_time}, '{monitor_info}')".format(**args)
    connection.execute(sqlstr)
    connection.commit()
    connection.close()

# 无需在此删除一组记录，记录的外键task_id设置为CASCADE

# ----------------------------------------------------------------------------------------------------------------------
# traffic_replay_webpage_current_tasks 表，django只会读取表的内容，daemon进程则会增加、删除、更新或读取记录

def select_all_tasks(sqlite_db_path: str):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    cursor = connection.execute(f"SELECT * FROM traffic_replay_webpage_current_tasks")
    result = cursor.fetchall()
    connection.close()
    return result

def delete_a_task(sqlite_db_path: str, task_id: str):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    connection.execute(f"DELETE FROM traffic_replay_webpage_current_tasks where task_id='{task_id}'")
    connection.commit()
    connection.close()

def add_a_task(sqlite_db_path: str, args:dict):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    sqlstr = "INSERT INTO traffic_replay_webpage_current_tasks (task_id, task_config_file_name, task_status, task_type, " \
             "task_extra_info, task_creation_time) VALUES ('{task_id}', '{task_config_file_name}', '{task_status}', "\
             "'{task_type}', '{task_extra_info}', {task_creation_time})".format(**args)
    connection.execute(sqlstr)
    connection.commit()
    connection.close()

def get_task_status(sqlite_db_path: str, task_id: str):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    cursor = connection.execute(f"SELECT task_status FROM traffic_replay_webpage_current_tasks WHERE task_id = '{task_id}'")
    result = cursor.fetchall()
    connection.close()
    return result

def update_task_status_stop(sqlite_db_path: str, task_id: str, info: dict):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    cursor = connection.execute(f"SELECT task_extra_info FROM traffic_replay_webpage_current_tasks WHERE task_id = '{task_id}'")
    result = cursor.fetchall()
    if len(result) == 0:
        connection.close()
        return
    task_extra_info = json.loads(base64_decodestr(result[0][0]))
    for key in info:
        task_extra_info[key] = info[key]
    task_extra_info = base64_encodestr(json.dumps(task_extra_info))
    sqlstr = f"UPDATE traffic_replay_webpage_current_tasks SET task_status = 'stopped', task_extra_info = '{task_extra_info}' WHERE task_id = '{task_id}'"
    connection.execute(sqlstr)
    connection.commit()
    connection.close()

def update_task_status_running(sqlite_db_path: str, task_id: str):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    sqlstr = f"UPDATE traffic_replay_webpage_current_tasks SET task_status = 'stopped', task_status = 'running' WHERE task_id = '{task_id}'"
    connection.execute(sqlstr)
    connection.commit()
    connection.close()

def get_task_primary_id(sqlite_db_path: str, task_id: str):
    connection = sqlite3.connect(sqlite_db_path, timeout=10)
    cursor = connection.execute(f"SELECT id FROM traffic_replay_webpage_current_tasks WHERE task_id = '{task_id}'")
    result = cursor.fetchall()
    connection.close()
    return result

def base64_encodestr(s: str):
    return bytes.decode(base64.b64encode(str.encode(s)))

def base64_decodestr(s: str):
    return bytes.decode(base64.b64decode(str.encode(s)))