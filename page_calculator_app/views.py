import datetime
import time
from functools import reduce

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from .forms import UploadFileForm
from .models import PrintFilesModel, EmployeeModel, OrdersModel, ObjectModel, ContractModel, CountTasksModel, \
    ListsFileModel, PrintPagePermissionModel
from .functions import check_date_in_db, check_color_pages
from print_service_app.tasks import celery_check_color_pages
from print_service_app.views import check_permission_user
from PIL import Image, ImageStat
from django.http import HttpResponse
import mimetypes
from django.http import HttpResponse

import json
import os
import ast

import math
import PyPDF2
from pdf2image import convert_from_path

# Словарь с размерами листов по ГОСТ
PAGE_SIZE_STANDARD = {
    'A0': (841, 1189, 16),
    'A0x2': (1189, 1682, 32),
    'A0x3': (1189, 2523, 48),
    'A1': (594, 841, 8),
    'A1x3': (841, 1783, 24),
    'A1x4': (841, 2378, 32),
    'A2': (420, 594, 4),
    'A2x3': (594, 1261, 12),
    'A2x4': (594, 1682, 16),
    'A2x5': (594, 2102, 20),
    'A3': (297, 420, 2),
    'A3x3': (420, 891, 6),
    'A3x4': (420, 1189, 8),
    'A3x5': (420, 1486, 10),
    'A3x6': (420, 1783, 12),
    'A3x7': (420, 2080, 14),
    'A4': (210, 297, 1),
    'A4x3': (297, 630, 3),
    'A4x4': (297, 841, 4),
    'A4x5': (297, 1051, 5),
    'A4x6': (297, 1261, 6),
    'A4x7': (297, 1471, 7),
    'A4x8': (297, 1682, 8),
    'A4x9': (297, 1892, 9),
}


def handle_uploaded_file(f):
    """
    Функция для загрузки файлов
    """
    with open(f"{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


class StartPageView(View):
    """Стартовая страница для редиректа на страницу авторизации"""

    def get(self, request):
        if request.user.is_authenticated:
            print(request.user)
            return redirect('index')
        else:
            return redirect('login')


class IndexView(View):
    """Главная страница"""

    def get(self, request):
        # В случае если в cookies не установлен допуск размера, установить +-15мм
        try:
            clearance = int(request.COOKIES['clearance'])
        except:
            clearance = 15
        # Проверка, есть ли у сотрудника права доступа к типографии
        try:
            user = EmployeeModel.objects.get(user=request.user)
            user_permission = PrintPagePermissionModel.objects.get(emp=user)
        except:
            user_permission = False
        form = UploadFileForm()  # Форма выгрузки файла
        # Данные для модального окна отправки файла на печать
        orders = OrdersModel.objects.get_queryset().order_by('order')
        objects = ObjectModel.objects.get_queryset().filter(show=True).order_by('object_name')
        content = {'form': form,
                   "orders": orders,
                   'clearance': clearance,
                   'objects': objects,
                   'user_permission': user_permission}
        return render(request, 'page_calculator_app/index.html', content)


class GetAnswerView(View):
    def post(self, request):
        # В случае если не установлен допуск размера, установить +-15мм
        try:
            clearance = int(request.COOKIES['clearance'])
        except:
            clearance = 15
        files_count = 0  # Счетчик файлов
        all_files_format = 0  # Счетчик форматов А4 по всем файлам
        all_lists_approve = 0  # Счетчик распознанных листов
        all_lists_count = 0  # Всего листов во всех файлах
        errors = 0  # Ошибок по файлам

        print(f'request.POST: {request.POST}')
        print(f'request.FILES: {request.FILES}')
        print(f'request.COOKIES: {request.COOKIES}')
        print('-----------------------')
        print(f'Подсчет с допуском {clearance}мм')
        print('-----------------------')

        # Итоговый словарь с перечнем файлов
        exit_dict = {}

        for file in request.FILES.getlist('file'):
            files_count += 1
            print(file, file.content_type)
            try:
                # Пустой словарь для подсчета листов
                pdf_size_file = {
                    'A0': 0,
                    'A0x2': 0,
                    'A0x3': 0,
                    'A1': 0,
                    'A1x3': 0,
                    'A1x4': 0,
                    'A2': 0,
                    'A2x3': 0,
                    'A2x4': 0,
                    'A2x5': 0,
                    'A3': 0,
                    'A3x3': 0,
                    'A3x4': 0,
                    'A3x5': 0,
                    'A3x6': 0,
                    'A3x7': 0,
                    'A4': 0,
                    'A4x3': 0,
                    'A4x4': 0,
                    'A4x5': 0,
                    'A4x6': 0,
                    'A4x7': 0,
                    'A4x8': 0,
                    'A4x9': 0,
                }
                pdf_unknown_size_file = {}  # Нераспознанные листы файла
                a4_count = 0  # Счетчик форматов А4
                normal_pages = 0  # Счетчик распознанных листов
                list_pages = []  # Список листов

                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                all_lists_count += num_pages
                for i in range(num_pages):
                    checker = 0  # В случае если размер по ГОСТ устанавливаем 1
                    box = pdf_reader.pages[i]
                    # Переводим значения в миллиметры
                    width = math.ceil(float(box.mediabox.width) * 0.35273159)
                    height = math.ceil(float(box.mediabox.height) * 0.35273159)
                    # list_pages.append([height, width])
                    # Приводим к одной ориентации
                    if width < height:
                        small = width
                        long = height
                    else:
                        small = height
                        long = width
                    # Проверяем вхождение данных размеров в стандартные, с допуском clearance
                    for key, value in PAGE_SIZE_STANDARD.items():
                        if (value[0] >= small - clearance) and (value[0] <= small + clearance) and (
                                value[1] <= long + clearance) and (
                                value[1] >= long - clearance):
                            normal_pages += 1
                            a4_count += value[2]
                            pdf_size_file[key] += 1
                            checker = 1
                            list_pages.append([height, width, key])
                    # Если в стандартные значения не вошли
                    if checker == 0:
                        size = f'{small}x{long}'
                        list_pages.append([height, width, 0])
                        try:
                            pdf_unknown_size_file[size] += 1  # Если такой размер уже есть в словаре
                        except:
                            pdf_unknown_size_file[size] = 1

                temp_list = []
                # Создаем словарь с пустыми значениями.
                for key, value in pdf_size_file.items():
                    if value == 0:
                        temp_list.append(key)
                # Удаляем из словаря все пустые значения
                for i in temp_list:
                    del pdf_size_file[i]
                final_list = []  # итоговый список по файлу
                for key, value in pdf_size_file.items():
                    if value > 0:
                        final_list.append([key, value])
                print(f'pdf_size_file {pdf_size_file}')
                good_lists = pdf_size_file.copy()

                num_pages = len(pdf_reader.pages)
                exit_dict[file.name] = pdf_size_file
                exit_dict[file.name]['good_lists'] = good_lists  # распознанные листы
                exit_dict[file.name]['count_pages'] = num_pages  # количество листов
                exit_dict[file.name]['pdf_unknown_size_file'] = pdf_unknown_size_file  # список нераспознанных листов
                exit_dict[file.name]['len_pdf_unknown_size_file'] = len(
                    pdf_unknown_size_file)  # количество нераспознанных листов
                exit_dict[file.name]['list_pages'] = list_pages  # список листов по файлу
                exit_dict[file.name]['normal_pages'] = normal_pages  # количество распознанных листов
                exit_dict[file.name]['a4_count'] = a4_count  # количество форматов А4
                all_lists_approve += normal_pages  # общее количество распознанных листов
                all_files_format += a4_count  # обшее количество форматов А4
            except:
                exit_dict[file.name] = {}  # Информация о файле, в случае если он не PDF
                exit_dict[file.name]['error'] = 1
                errors += 1
            print('-----------------------')
        content = {'all_lists_count': all_lists_count,
                   'files_count': files_count,
                   'all_lists_approve': all_lists_approve,
                   'all_files_format': all_files_format,
                   'exit_dict': exit_dict,
                   'clearance': clearance,
                   'errors': errors,
                   'good_files': files_count - errors,
                   }
        resp = render(request, 'page_calculator_app/answer.html', content)
        resp.set_cookie(key='clearance', value=clearance)  # Установка допуска clearance в cookie
        return resp


class ChangeClearanceView(View):
    def post(self, request):
        """
        Для ajax запроса на редактирование допуска clearance
        """
        clearance = int(request.POST.get('input_clearance_value'))
        print(clearance)
        print(f'request.POST: {request.POST}')
        print(f'request.FILES: {request.FILES}')
        print(f'request.COOKIES: {request.COOKIES}')
        resp = HttpResponse(status=200)
        resp.set_cookie('clearance', clearance)
        return resp


# class GetBlancView(View):
#     def get(self, request):
#         print(f'request.GET: {request.GET}')
#         print(f'request.FILES: {request.FILES}')
#         print(f'request.COOKIES: {request.COOKIES}')
#         json_result = request.GET['json']
#         print(json_result)
#         print(type(json_result))
#         dict_result = ast.literal_eval(json_result)
#         print(dict_result)
#         print(type(dict_result))
#
#         return HttpResponse(status=200)


class PrintView(View):
    """Отправка файлов на печать"""
    def post(self, request):
        print(f'request.user: {request.user}')
        print(f'request.POST: {request.POST}')
        print(f'request.FILES: {request.FILES}')
        print(f'request.FILES: {request.FILES["file"]}')
        print(f'request.COOKIES: {request.COOKIES}')
        start_time = time.time()
        # Формируем запись со счетчиком заявок в день
        check_date_in_db()
        last_task_in_db = CountTasksModel.objects.latest('id')
        last_task_in_db.count += 1
        last_task_in_db.save()
        user_clearance = int(request.COOKIES['clearance'])
        new_task_to_print = PrintFilesModel(
            filename=request.FILES['file'].name,
            inventory_number_file=request.POST.get('input_inventory_number_file_value'),
            order_id=request.POST.get('order_id'),
            object_id=request.POST.get('object_id'),
            contract_id=request.POST.get('contract_id'),
            file_to_print=request.FILES['file'],
            copy_count=int(request.POST.get('copy_count_value')),
            task_type_work=request.POST.get('TypeWorkTask_id'),
            emp_upload_file_id=EmployeeModel.objects.get(user=request.user).id,
            inventory_number_request=f'{last_task_in_db.date_of_print}-{last_task_in_db.count}',
            type_task=2,
            count_pages=request.POST.get('temp_file_count_pages'),
            a4_count_formats=int(request.POST.get('temp_file_a4_formats')),
            print_folding=int(request.POST.get('folding_id')),
            user_clearance=user_clearance,
            color=int(request.POST.get('color_id')),
        )
        new_task_to_print.save()
        print(f"Сохранили задачу в базу за {time.time() - start_time} секунд от момента старта")
        json_all_lists_file = request.POST.get('temp_all_lists_file')
        all_lists_file = ast.literal_eval(json_all_lists_file)

        # Создаем записи о листах
        temp_file_json = request.POST['temp_file_json']
        dict_temp_file_json = ast.literal_eval(temp_file_json)
        temp_file_bad_json = request.POST['temp_file_bad_json']

        print_files_info = ListsFileModel()
        print_files_info.print_file_id = new_task_to_print.id

        # Вносим все листы в базу данных

        if 'A0' in dict_temp_file_json:
            print_files_info.a0 = dict_temp_file_json['A0']
        if 'A0x2' in dict_temp_file_json:
            print_files_info.a0x2 = dict_temp_file_json['A0x2']
        if 'A0x3' in dict_temp_file_json:
            print_files_info.a0x3 = dict_temp_file_json['A0x3']
        if 'A1' in dict_temp_file_json:
            print_files_info.a1 = dict_temp_file_json['A1']
        if 'A1x3' in dict_temp_file_json:
            print_files_info.a1x3 = dict_temp_file_json['A1x3']
        if 'A1x4' in dict_temp_file_json:
            print_files_info.a1x4 = dict_temp_file_json['A1x4']
        if 'A2' in dict_temp_file_json:
            print_files_info.a2 = dict_temp_file_json['A2']
        if 'A2x3' in dict_temp_file_json:
            print_files_info.a2x3 = dict_temp_file_json['A2x3']
        if 'A2x4' in dict_temp_file_json:
            print_files_info.a2x4 = dict_temp_file_json['A2x4']
        if 'A2x5' in dict_temp_file_json:
            print_files_info.a2x5 = dict_temp_file_json['A2x5']
        if 'A3' in dict_temp_file_json:
            print_files_info.a3 = dict_temp_file_json['A3']
        if 'A3x3' in dict_temp_file_json:
            print_files_info.a3x3 = dict_temp_file_json['A3x3']
        if 'A3x4' in dict_temp_file_json:
            print_files_info.a3x4 = dict_temp_file_json['A3x4']
        if 'A3x5' in dict_temp_file_json:
            print_files_info.a3x5 = dict_temp_file_json['A3x5']
        if 'A3x6' in dict_temp_file_json:
            print_files_info.a3x6 = dict_temp_file_json['A3x6']
        if 'A3x7' in dict_temp_file_json:
            print_files_info.a3x7 = dict_temp_file_json['A3x7']
        if 'A4' in dict_temp_file_json:
            print_files_info.a4 = dict_temp_file_json['A4']
        if 'A4x3' in dict_temp_file_json:
            print_files_info.a4x3 = dict_temp_file_json['A4x3']
        if 'A4x4' in dict_temp_file_json:
            print_files_info.a4x4 = dict_temp_file_json['A4x4']
        if 'A4x5' in dict_temp_file_json:
            print_files_info.a4x5 = dict_temp_file_json['A4x5']
        if 'A4x6' in dict_temp_file_json:
            print_files_info.a4x6 = dict_temp_file_json['A4x6']
        if 'A4x7' in dict_temp_file_json:
            print_files_info.a4x7 = dict_temp_file_json['A4x7']
        if 'A4x8' in dict_temp_file_json:
            print_files_info.a4x8 = dict_temp_file_json['A4x8']
        if 'A4x9' in dict_temp_file_json:
            print_files_info.a4x9 = dict_temp_file_json['A4x9']
        # Нераспознанные листы
        print_files_info.other_pages = temp_file_bad_json
        print_files_info.save()
        print(f"Сохранили все листы в базу за {time.time() - start_time} секунд от момента старта")
        file_path = new_task_to_print.file_to_print.path
        # Если пользователь выбрал цветную печать, отправляем в Celery разбирать цветные и чб листы
        if int(request.POST.get('color_id')) == 1:
            celery_check_color_pages.delay(file_path=file_path, all_lists_file=all_lists_file,
                                           lists_file_id=print_files_info.id)
        return HttpResponse(status=200)


class MyPrintTaskView(View):
    """Список заданий на печать сотрудника"""
    def get(self, request):
        user_permission = check_permission_user(request.user)
        emp = EmployeeModel.objects.get(user=request.user)
        emp_tasks = PrintFilesModel.objects.get_queryset().filter(emp_upload_file=emp).order_by('-id')
        content = {'emp': emp,
                   'emp_tasks': emp_tasks,
                   "user_permission": user_permission}
        return render(request, 'page_calculator_app/my-print-task.html', content)


def get_contracts(request):
    """ajax для получения договоров по заказу"""
    print(request.GET)
    object_id = int(request.GET.get('object'))
    contracts = ContractModel.objects.get_queryset().filter(contract_object_id=object_id).filter(show=True).order_by(
        'contract_name')
    content = {'contracts': contracts}
    return render(request, 'page_calculator_app/ajax/load_contracts.html', content)


class GetInfoMyTaskView(View):
    """Просмотр деталей задания для сотрудника"""
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
        return render(request, 'page_calculator_app/ajax/my_modal_details_task.html', content)


class CancelMyTaskView(View):
    """Отмена задания на печать сотрудником"""
    def post(self, request):
        print(request.POST)
        cancel_print_task_id = request.POST['number_task']
        cancel_print_task_obj = PrintFilesModel.objects.get(id=cancel_print_task_id)
        cancel_print_task_obj.status = 0
        cancel_print_task_obj.date_change_status = datetime.datetime.now()
        file_path = os.path.join(settings.MEDIA_ROOT, str(cancel_print_task_obj.file_to_print))
        if os.path.exists(file_path):
            os.remove(file_path)
        cancel_print_task_obj.file_to_print = None
        cancel_print_task_obj.save()
        return HttpResponse(status=200)


class DeleteFileView(View):
    def get(self, request, pk):
        today = datetime.datetime.today()
        count_tasks = 0
        count_delete_tasks_files = 0
        all_print_tasks = PrintFilesModel.objects.get_queryset().filter(status=3)
        for task in all_print_tasks:
            task_date = task.date_change_status.date()
            task_date_delta = (today - task_date).days
            count_tasks += 1
            if task_date_delta > 7:
                file_path = os.path.join(settings.MEDIA_ROOT, str(task.file_to_print))
                if os.path.exists(file_path):
                    os.remove(file_path)
                task.file_to_print = None
                task.save()
        return HttpResponse(status=200)
