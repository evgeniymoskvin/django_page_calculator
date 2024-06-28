import ast
import datetime
import json

from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.encoding import escape_uri_path
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import DateField

import mimetypes
import os.path

from .tasks import celery_email_print_done
from page_calculator_app.functions import save_status_log

from docxtpl import DocxTemplate

from random import randint
from page_calculator_app.models import PrintFilesModel, ListsFileModel, EmployeeModel, PrintPagePermissionModel, \
    ChangeStatusHistoryModel


def check_permission_user(req_user):
    """
    Проверка прав доступа у сотрудника
    """
    try:
        user = EmployeeModel.objects.get(user=req_user)
        user_permission = PrintPagePermissionModel.objects.get(emp=user)
    except Exception as e:
        print(e)
        user_permission = False
    return user_permission


class IndexView(View):
    """Главная страница раздела типографии"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        user_permission = check_permission_user(request.user)
        content = {"tasks_to_print": "Идет загрузка",
                   "user_permission": user_permission}
        if user_permission:
            return render(request, 'print_service_app/new-tasks.html', content)
        else:
            # в случае если у человека нет доступа к типографии
            return render(request, 'print_service_app/permission-error.html', content)


def get_tasks(request):
    """Функция для ajax запроса, обновляющегося с периодичностью,
    что бы показывать текущие задачи в реальном времени"""
    tasks_to_print = PrintFilesModel.objects.get_queryset().filter(Q(status=1) | Q(status=2)).order_by('-id')
    content = {"tasks_to_print": tasks_to_print}
    return render(request, 'print_service_app/ajax/get_task_list.html', content)

class GetInfoPrintTaskView(View):
    """
    Информация по конкретному заданию
    """

    def get(self, request):
        obj_id = int(request.GET.get('object'))
        obj = PrintFilesModel.objects.get(id=obj_id)
        # Проверка на случай, если в базе отсутствует информация о листах
        try:
            obj_info = ListsFileModel.objects.get(print_file_id=obj.id)
            bad_lists = obj_info.other_pages
            dict_temp_file_json = ast.literal_eval(bad_lists)
        except Exception as e:
            print(e)
            obj_info = None
            dict_temp_file_json = {}

        content = {'obj': obj,
                   'obj_info': obj_info,
                   'bad_lists': dict_temp_file_json}
        return render(request, 'print_service_app/ajax/modal_details_task.html', content)

    def post(self, request):
        """
        Изменение статуса задачи сотрудником типографии
        """
        print(request.POST)
        emp = EmployeeModel.objects.get(user=request.user)
        print_task_id = request.POST['obj_id_for_change_status']
        print_task_obj = PrintFilesModel.objects.get(id=print_task_id)
        print_task_obj.status = int(request.POST['TypeWorkTask_id'])
        print_task_obj.date_change_status = datetime.datetime.now()
        print_task_obj.save()
        # Записываем в лог
        save_status_log(print_task_id=print_task_id, print_task_status=print_task_obj.status, emp_id=emp.id)
        # Отправка письма через Celery
        if int(request.POST['TypeWorkTask_id']) == 3:
            celery_email_print_done.delay(int(print_task_id))
        return HttpResponse(status=200)


class GetInfoReportPrintTaskView(View):
    def get(self, request):
        obj_id = int(request.GET.get('object'))
        obj = PrintFilesModel.objects.get(id=obj_id)
        # Проверка на случай, если в базе отсутствует информация о листах
        try:
            obj_info = ListsFileModel.objects.get(print_file_id=obj.id)
            bad_lists = obj_info.other_pages
            dict_temp_file_json = ast.literal_eval(bad_lists)
        except Exception as e:
            print(e)
            obj_info = None
            dict_temp_file_json = {}

        content = {'obj': obj,
                   'obj_info': obj_info,
                   'bad_lists': dict_temp_file_json}
        return render(request, 'print_service_app/ajax/modal_report_details_task.html', content)

class DownloadFileView(View):
    """Скачивание файла"""

    def get(self, request, pk):
        file_path_in_db = PrintFilesModel.objects.get(id=pk)
        file_path_in_db.status = 2
        file_path_in_db.save()
        emp = EmployeeModel.objects.get(user=request.user)
        save_status_log(print_task_id=pk, print_task_status=file_path_in_db.status, emp_id=emp.id)
        # print(file_path_in_db.file)
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_path_in_db.file_to_print))
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(file_path)
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=' + escape_uri_path(os.path.basename(file_path))
                return response
        raise Http404


class DownloadBlankView(View):
    """Скачивание заявки на печать"""

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
            lists_info = ''
            color_pages = 0
            if pages_info.a4 > 0:
                lists_info += f'A4 - {pages_info.a4}\n'
            if pages_info.a4_color > 0:
                lists_info += f'A4 цветной - {pages_info.a4_color}\n'
                color_pages += pages_info.a4_color
            if pages_info.a3 > 0:
                lists_info += f'A3 - {pages_info.a3}\n'
            if pages_info.a3_color > 0:
                lists_info += f'A3 цветной - {pages_info.a3_color}\n'
                color_pages += pages_info.a3_color
            if pages_info.a2 > 0:
                lists_info += f'A2 - {pages_info.a2}\n'
            if pages_info.a2_color > 0:
                lists_info += f'A2 цветной - {pages_info.a2_color}\n'
                color_pages += pages_info.a2_color
            if pages_info.a1 > 0:
                lists_info += f'A1 - {pages_info.a1}\n'
            if pages_info.a1_color > 0:
                lists_info += f'A1 цветной - {pages_info.a1_color}\n'
                color_pages += pages_info.a1_color
            if pages_info.a0 > 0:
                lists_info += f'A0 - {pages_info.a0}\n'
            if pages_info.a0_color > 0:
                lists_info += f'A0 цветной - {pages_info.a0_color}\n'
                color_pages += pages_info.a0_color
            if pages_info.a4x3 > 0:
                lists_info += f'A4x3 - {pages_info.a4x3}\n'
            if pages_info.a4x3_color > 0:
                lists_info += f'A4x3 цветной - {pages_info.a4x3_color}\n'
                color_pages += pages_info.a4x3_color
            if pages_info.a4x4 > 0:
                lists_info += f'A4x4 - {pages_info.a4x4}\n'
            if pages_info.a4x4_color > 0:
                lists_info += f'A4x4 цветной - {pages_info.a4x4_color}\n'
                color_pages += pages_info.a4x4_color
            if pages_info.a4x5 > 0:
                lists_info += f'A4x5 - {pages_info.a4x5}\n'
            if pages_info.a4x5_color > 0:
                lists_info += f'A4x5 цветной - {pages_info.a4x5_color}\n'
                color_pages += pages_info.a4x5_color
            if pages_info.a4x6 > 0:
                lists_info += f'A4x6 - {pages_info.a4x6}\n'
            if pages_info.a4x6_color > 0:
                lists_info += f'A4x6 цветной - {pages_info.a4x6_color}\n'
                color_pages += pages_info.a4x6_color
            if pages_info.a4x7 > 0:
                lists_info += f'A4x7 - {pages_info.a4x7}\n'
            if pages_info.a4x7_color > 0:
                lists_info += f'A4x7 цветной - {pages_info.a4x7_color}\n'
                color_pages += pages_info.a4x7_color
            if pages_info.a4x8 > 0:
                lists_info += f'A4x8 - {pages_info.a4x8}\n'
            if pages_info.a4x8_color > 0:
                lists_info += f'A4x8 цветной - {pages_info.a4x8_color}\n'
                color_pages += pages_info.a4x8_color
            if pages_info.a4x9 > 0:
                lists_info += f'A4x9 - {pages_info.a4x9}\n'
            if pages_info.a4x9_color > 0:
                lists_info += f'A4x9 цветной - {pages_info.a4x9_color}\n'
                color_pages += pages_info.a4x9_color
            if pages_info.a3x3 > 0:
                lists_info += f'A3x3 - {pages_info.a3x3}\n'
            if pages_info.a3x3_color > 0:
                lists_info += f'A3x3 цветной - {pages_info.a3x3_color}\n'
                color_pages += pages_info.a3x3_color
            if pages_info.a3x4 > 0:
                lists_info += f'A3x4 - {pages_info.a3x4}\n'
            if pages_info.a3x4_color > 0:
                lists_info += f'A3x4 цветной - {pages_info.a3x4_color}\n'
                color_pages += pages_info.a3x4_color
            if pages_info.a3x5 > 0:
                lists_info += f'A3x5 - {pages_info.a3x5}\n'
            if pages_info.a3x5_color > 0:
                lists_info += f'A3x5 цветной - {pages_info.a3x5_color}\n'
                color_pages += pages_info.a3x5_color
            if pages_info.a3x6 > 0:
                lists_info += f'A3x6 - {pages_info.a3x6}\n'
            if pages_info.a3x6_color > 0:
                lists_info += f'A3x6 цветной - {pages_info.a3x6_color}\n'
                color_pages += pages_info.a3x6_color
            if pages_info.a3x7 > 0:
                lists_info += f'A3x7 - {pages_info.a3x7}\n'
            if pages_info.a3x7_color > 0:
                lists_info += f'A3x7 цветной - {pages_info.a3x7_color}\n'
                color_pages += pages_info.a3x7_color
            if pages_info.a2x3 > 0:
                lists_info += f'A2x3 - {pages_info.a2x3}\n'
            if pages_info.a2x3_color > 0:
                lists_info += f'A2x3 цветной - {pages_info.a2x3_color}\n'
                color_pages += pages_info.a2x3_color
            if pages_info.a2x4 > 0:
                lists_info += f'A2x4 - {pages_info.a2x4}\n'
            if pages_info.a2x4_color > 0:
                lists_info += f'A2x4 цветной - {pages_info.a2x4_color}\n'
                color_pages += pages_info.a2x4_color
            if pages_info.a2x5 > 0:
                lists_info += f'A2x5 - {pages_info.a2x5}\n'
            if pages_info.a2x5_color > 0:
                lists_info += f'A2x5 цветной - {pages_info.a2x5_color}\n'
                color_pages += pages_info.a2x5_color
            if pages_info.a1x3 > 0:
                lists_info += f'A1x3 - {pages_info.a1x3}\n'
            if pages_info.a1x3_color > 0:
                lists_info += f'A1x3 цветной - {pages_info.a1x3_color}\n'
                color_pages += pages_info.a1x3_color
            if pages_info.a1x4 > 0:
                lists_info += f'A1x4 - {pages_info.a1x4}\n'
            if pages_info.a1x4_color > 0:
                lists_info += f'A1x4 цветной - {pages_info.a1x4_color}\n'
                color_pages += pages_info.a1x4_color
            if pages_info.a0x2 > 0:
                lists_info += f'A0x2 - {pages_info.a0x2}\n'
            if pages_info.a0x2_color > 0:
                lists_info += f'A0x2 цветной - {pages_info.a0x2_color}\n'
                color_pages += pages_info.a0x2_color
            if pages_info.a0x3 > 0:
                lists_info += f'A0x3 - {pages_info.a0x3}\n'
            if pages_info.a0x3_color > 0:
                lists_info += f'A0x3 цветной - {pages_info.a0x3_color}\n'
                color_pages += pages_info.a0x3_color
            dict_temp_file_json = eval(pages_info.other_pages)
            for key, value in dict_temp_file_json.items():
                lists_info += f'{key} - {value}\n'
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
                       "info": f'{color_info}',
                       'lists_info': lists_info,
                       'color': color_pages,
                       "a4f": print_task.a4_count_formats}
            doc.render(content)
            new_full_path = os.path.join(settings.BASE_DIR, 'print_service_app', 'docx', 'zaiavka_done.docx')
            doc.save(new_full_path)
            file_name = f'{str(print_task.inventory_number_file)}.docx'
            print(file_name)
            with open(new_full_path, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(new_full_path)
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=' + escape_uri_path(file_name)
                return response
        raise Http404


class AllTaskView(View):
    """Просмотр всех заданий на печать"""

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


class ReportView(View):
    """Страница для формирования отчета"""

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        print(f'request.user: {request.user}')
        print(f'request.POST: {request.POST}')
        user_permission = check_permission_user(request.user)
        if user_permission:
            content = {"user_permission": user_permission}
            return render(request, 'print_service_app/report.html', content)
        else:
            content = {}
            return render(request, 'print_service_app/permission-error.html', content)

    def post(self, request):
        print(f'request.POST: {request.POST}')
        start_date = datetime.datetime.strptime(request.POST.get('date_start'), "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(request.POST.get('date_end'), "%Y-%m-%d").date()
        end_date += datetime.timedelta(days=1)
        print(f'Запрошен отчет на даты: {start_date} - {end_date}')
        search_result = PrintFilesModel.objects.get_queryset()
        if start_date:
            search_result = search_result.filter(add_file_date__gte=start_date)
        if end_date:
            search_result = search_result.filter(add_file_date__lte=end_date)
        search_result = search_result.filter(status=3).order_by('-id')
        content = {'search_result': search_result,
                   'start_date': request.POST.get('date_start'),
                   'end_date': request.POST.get('date_end')}
        # return HttpResponse(status=200)
        return render(request, 'print_service_app/ajax/result-report.html', content)
