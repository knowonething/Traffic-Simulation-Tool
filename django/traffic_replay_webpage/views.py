import time

from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse

import json
import base64
import os

from traffic_replay_webpage.models import current_tasks, request_queue, traffic_recorders, config_files, fs

# 主页
def index(request):
    context = {}
    return render(request, 'traffic_replay_webpage/index.html', context)


# 生成流量页面
def generate(request):
    context = {}
    return render(request, 'traffic_replay_webpage/generate.html', context)


# 容器模拟用户流量界面
def simulate(request):
    context = {}
    return render(request, 'traffic_replay_webpage/simulate.html', context)


# 监视流量界面
def monitor(request):
    context = {}
    return render(request, 'traffic_replay_webpage/monitor.html', context)


# 管理文件界面
def manage_files(request):
    context = {}
    return render(request, 'traffic_replay_webpage/manage-files.html', context)


def get_tasks(request):
    if request.method != "POST":
        return JsonResponse([])

    task_type = request.POST["task_type"]

    result = current_tasks.objects.filter(task_type=task_type)

    return_data = []
    for item in result:
        new_data = {
            "task_id": item.task_id,
            "task_config_file_name": item.task_config_file_name,
            "task_status": item.task_status,
            "task_extra_info": item.task_extra_info,
            "task_creation_time": item.task_creation_time,
        }
        return_data.append(new_data)
    return JsonResponse(return_data, safe=False)


def get_configs(request):
    if request.method != "POST":
        return JsonResponse([])

    file_usage = request.POST["file_usage"]

    result = config_files.objects.filter(file_usage=file_usage)

    return_data = []
    for item in result:
        new_data = {
            "file_name": item.file_name,
            "file_creation_time": item.file_creation_time,
            "file_description": item.file_description,
        }
        return_data.append(new_data)
    return JsonResponse(return_data, safe=False)


def get_records(request):
    if request.method != "POST":
        return JsonResponse([])

    task_id = request.POST["task_id"]
    result = current_tasks.objects.filter(task_id=task_id)
    if len(result) == 0:
        return JsonResponse([])
    related_task_id = result[0].id
    time_after = request.POST["time_after"]
    result = traffic_recorders.objects.filter(related_task_id=related_task_id, recorder_time__gt=time_after)
    print(task_id, related_task_id, time_after, len(result))
    data = []
    for item in result:
        data.append([item.recorder_time, item.monitor_info])
    return JsonResponse(data, safe=False)


def request(request):
    if request.method != "POST":
        return JsonResponse([])

    request_action = request.POST["action"]
    request_args = request.POST["request_args"]
    print(request_args)
    request_execution_time = request.POST["execution_time"]
    new_obj = request_queue(request_action=request_action, request_args=request_args, request_execution_time=request_execution_time)
    new_obj.save()
    return JsonResponse({"result": "success"})

def upload_file(request):
    if request.method != "POST":
        return JsonResponse({})
    file_usage = request.POST["usage"]
    file_description = request.POST["file_desc"]
    failed_files = []
    for file_obj in request.FILES.getlist("file"):
        file_name = file_obj.name
        result = config_files.objects.filter(file_usage=file_usage, file_name=file_name)
        if len(result) != 0:
            failed_files.append(file_name)
            continue
        new_file = config_files(file_usage=file_usage, file_name=file_name, file_description=file_description, file_creation_time=time.time(), file_obj=file_obj)
        new_file.save()

    return JsonResponse(failed_files, safe=False)

def get_content(request):
    if request.method != "POST":
        return JsonResponse([])

    file_usage = request.POST["file_usage"]
    file_name = request.POST["file_name"]
    result = config_files.objects.filter(file_usage=file_usage, file_name=file_name)

    if len(result) == 0:  # 找不到文件的情况之后处理
        return HttpResponse("")

    data = result[0].file_obj.read()

    return HttpResponse(data)

def delete_file(request):
    if request.method != "POST":
        return JsonResponse([])
    fail_files = []
    for name in request.POST:
        file_usage = request.POST[name]
        file_name = name
        result = config_files.objects.filter(file_usage=file_usage, file_name=file_name)

        if len(result) == 0:
            fail_files.append(name)
            continue

        file = result[0]
        filepath = file.file_obj.path
        try:
            fs.delete(filepath)
            file.delete()
        except:
            fail_files.append(name)
    return JsonResponse(fail_files, safe=False)


def base64_encodestr(s: str):
    return bytes.decode(base64.b64encode(str.encode(s)))
