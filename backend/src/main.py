from util.task_service import TaskService

if __name__ == "__main__":
    TS = TaskService("!sqlite文件的路径!", "!配置文件的路径!")
    TS.run_server()

