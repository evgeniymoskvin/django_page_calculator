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

from .tasks import celery_email_print_done

from docxtpl import DocxTemplate

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
        # Отправка письма через Celery
        if int(request.POST['TypeWorkTask_id']) == 3:
            celery_email_print_done(int(print_task_id))
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


class DownloadBlankView(View):
    def get(self, request, pk):
        file_docx_path = os.path.join(settings.BASE_DIR, 'print_service_app', 'docx', 'zaiavka.docx')
        print(file_docx_path)
        if os.path.exists(file_docx_path):
            doc = DocxTemplate(file_docx_path)
            print_task = PrintFilesModel.objects.get(id=pk)
            pages_info = ListsFileModel.objects.get(print_file=print_task)
            try:
                contract = str(print_task.contract.contract_name)[:20]
            except Exception as e:
                print(e)
                contract = ''
            if print_task.color:
                color_info = f'Цветной'
            else:
                color_info = f''

            other_info = f'{pages_info.other_pages}'
            content = {"request_number": print_task.inventory_number_request,
                       "day": datetime.datetime.now().day,
                       "month": datetime.datetime.now().strftime('%b'),
                       "year": datetime.datetime.now().year,
                       "order": print_task.order.order,
                       "contract": contract,
                       "emp_group": print_task.emp_upload_file.department.command_number,
                       "tel": print_task.emp_upload_file.user_phone,
                       "emp": f'{print_task.emp_upload_file.last_name} {str(print_task.emp_upload_file.first_name)[:1]}. {str(print_task.emp_upload_file.middle_name)[:1]}.',
                       "all": print_task.count_pages,
                       "cop": print_task.copy_count,
                       "inventory_number": print_task.inventory_number_file,
                       "a4": pages_info.a4,
                       "a3": pages_info.a3,
                       "a2": pages_info.a2,
                       "a1": pages_info.a1,
                       "a0": pages_info.a0,
                       "a4x": int(pages_info.a4x3) * 3 + int(pages_info.a4x4) * 4 + int(pages_info.a4x5) * 5 + int(
                           pages_info.a4x6) * 6 + int(pages_info.a4x7) * 7 + int(pages_info.a4x8) * 8 + int(
                           pages_info.a4x9) * 9,
                       "a3x": int(pages_info.a3x3) * 3 + int(pages_info.a3x4) * 4 + int(pages_info.a3x5) * 5 + int(
                           pages_info.a3x6) * 6 + int(pages_info.a3x7) * 7,
                       "a2x": int(pages_info.a2x3) * 3 + int(pages_info.a2x4) * 4 + int(pages_info.a2x5) * 5,
                       "a1x": int(pages_info.a1x3) * 3 + int(pages_info.a1x4) * 4,
                       "a0x": int(pages_info.a0x2) * 2 + int(pages_info.a0x3) * 3,
                       "info": f'{pages_info.other_pages}. {color_info}',
                       "a4f": print_task.a4_count_formats}
            doc.render(content)
            new_full_path = os.path.join(settings.BASE_DIR, 'print_service_app', 'docx', 'zaiavka_done.docx')
            doc.save(new_full_path)
            file_name = f'{str(print_task.inventory_number_file)}.docx'
            print(file_name)
            with open(new_full_path, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(new_full_path)
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'inline; filename=' + escape_uri_path(file_name)
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
