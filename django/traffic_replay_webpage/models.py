from django.db import models
from django.core.files.storage import FileSystemStorage

# Create your models here.

# 包含当前各项流量任务的信息的表
class current_tasks(models.Model):
    task_id = models.CharField(max_length=200, unique=True)  # 任务id
    task_config_file_name = models.CharField(max_length=200)  # 配置文件的路径
    task_status = models.CharField(max_length=200)  # 任务状态
    task_type = models.CharField(max_length=200)  # 任务类型
    task_extra_info = models.CharField(max_length=1000)  # 任务的额外信息
    task_creation_time = models.FloatField()  # 任务被创建的时间

class request_queue(models.Model):
    request_action = models.CharField(max_length=200)  # 等待执行的请求
    request_args = models.CharField(max_length=1000)  # 额外的参数
    request_execution_time = models.FloatField()  # 请求延期执行的时间

class traffic_recorders(models.Model):
    related_task = models.ForeignKey(current_tasks, on_delete=models.CASCADE)
    recorder_time = models.FloatField()
    monitor_info = models.CharField(max_length=1000)

fs = FileSystemStorage(location='!保存配置文件的路径!')

class config_files(models.Model):
    file_usage = models.CharField(max_length=200)
    file_name = models.CharField(max_length=200)
    file_creation_time = models.FloatField()
    file_description = models.CharField(max_length=1000)
    file_obj = models.FileField(storage=fs)


