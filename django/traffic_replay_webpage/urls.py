from django.urls import path

from . import views

app_name = 'traffic_replay_webpage'
urlpatterns = [
    path('', views.index, name="index"),
    path("generate/", views.generate, name="generate"),
    path("simulate/", views.simulate, name="simulate"),
    path("monitor/", views.monitor, name="monitor"),
    path("manage-files/", views.manage_files, name="manage-files"),
    path("get-tasks/", views.get_tasks, name="get-tasks"),
    path("get-configs/", views.get_configs, name="get-configs"),
    path("get-records/", views.get_records, name="get-records"),
    path("get-content/", views.get_content, name="get-content"),
    path("request/", views.request, name="request"),
    path("upload-file/", views.upload_file, name="upload-file"),
    path("delete-file/", views.delete_file, name="delete-file"),
]
