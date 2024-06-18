import ast
import datetime

from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.encoding import escape_uri_path

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

import mimetypes
import os.path

from random import randint
from page_calculator_app.models import PrintFilesModel, ListsFileModel, EmployeeModel, PrintPagePermissionModel


def check_permission_user(req_user):
    try:
        user = EmployeeModel.objects.get(user=req_user)
        user_permission = PrintPagePermissionModel.objects.get(emp=user)
    except:
        user_permission = False
    return user_permission


# Create your views here.

class IndexView(View):
    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user_permission = check_permission_user(request.user)
        content = {"tasks_to_print": "Идет загрузка",
                   "user_permission": user_permission}
        if user_permission:
            return render(request, 'print_service_app/new-tasks.html', content)
        else:
            return render(request, 'print_service_app/permission-error.html', content)


def get_tasks(request):
    # print('сработал функция get_tasks')
    # value = randint(1, 100)
    # content = {'value': value}

    tasks_to_print = PrintFilesModel.objects.get_queryset().filter(Q(status=1) | Q(status=2)).order_by('-id')
    content = {"tasks_to_print": tasks_to_print}

    return render(request, 'print_service_app/ajax/get_task_list.html', content)


class GetInfoPrintTaskView(View):
    def get(self, request):
        obj_id = int(request.GET.get('object'))
        obj = PrintFilesModel.objects.get(id=obj_id)
        try:
            obj_info = ListsFileModel.objects.get(print_file_id=obj.id)
            bad_lists = obj_info.other_pages
            dict_temp_file_json = ast.literal_eval(bad_lists)
        except:
            obj_info = None
            dict_temp_file_json = {}

        content = {'obj': obj,
                   'obj_info': obj_info,
                   'bad_lists': dict_temp_file_json}
        return render(request, 'print_service_app/ajax/modal_details_task.html', content)

    def post(self, request):
        print(request.POST)
        print_task_id = request.POST['obj_id_for_change_status']
        print_task_obj = PrintFilesModel.objects.get(id=print_task_id)
        print_task_obj.status = int(request.POST['TypeWorkTask_id'])
        print_task_obj.date_change_status = datetime.datetime.now()
        print_task_obj.save()
        return HttpResponse(status=200)


class DownloadFileView(View):
    def get(self, request, pk):
        file_path_in_db = PrintFilesModel.objects.get(id=pk)
        file_path_in_db.status = 2
        file_path_in_db.save()
        # print(file_path_in_db.file)
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_path_in_db.file_to_print))
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(file_path)
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'inline; filename=' + escape_uri_path(os.path.basename(file_path))
                return response
        raise Http404


class AllTaskView(View):
    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user_permission = check_permission_user(request.user)
        if user_permission:
            all_tasks = PrintFilesModel.objects.get_queryset().order_by('-id')
            content = {"all_tasks": all_tasks,
                       "user_permission": user_permission}
            return render(request, 'print_service_app/all-print-task.html', content)
        else:
            content = {}
            return render(request, 'print_service_app/permission-error.html', content)
