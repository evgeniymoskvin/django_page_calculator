import ast
import datetime
from copy import copy

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

from .tasks import celery_email_print_done, celery_email_print_cancel
from page_calculator_app.functions import save_status_log
from .functions import get_print_report_xls, get_dispatcher_report_xls

from docxtpl import DocxTemplate

from page_calculator_app.models import PrintFilesModel, ListsFileModel, EmployeeModel, PrintPagePermissionModel, \
    ChangeStatusHistoryModel, OrdersModel, ObjectModel, ContractModel, MarkDocModel


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
        user_permission = check_permission_user(request.user)  # Проверка прав пользователя
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
    # Задачи в статусе "Актуальные" и "В работе"
    content = {"tasks_to_print": tasks_to_print,
               'count_of_tasks': tasks_to_print.count()}
    return render(request, 'print_service_app/ajax/get_task_list.html', content)

def get_tasks_count(request):
    """Функция для ajax запроса, получения количества не обработанных задач"""
    tasks_to_print = PrintFilesModel.objects.get_queryset().filter(Q(status=1) | Q(status=2)).order_by('-id')
    # Задачи в статусе "Актуальные" и "В работе"
    return HttpResponse(tasks_to_print.count())


def get_task_info(obj_id):
    """Функция, для получения информации по конкретной задаче"""
    obj = PrintFilesModel.objects.get(id=obj_id)
    # Проверка на случай, если в базе отсутствует информация о листах
    try:
        obj_info = ListsFileModel.objects.get(print_file_id=obj.id)
        # Считаем количество цветных листов
        color_pages = obj_info.a0_color + obj_info.a0x2_color + obj_info.a0x3_color + obj_info.a1_color + obj_info.a1x3_color + obj_info.a1x4_color + obj_info.a2_color + obj_info.a2x3_color + obj_info.a2x4_color + obj_info.a2x5_color + obj_info.a3_color + obj_info.a3x3_color + obj_info.a3x4_color + obj_info.a3x5_color + obj_info.a3x6_color + obj_info.a3x7_color + obj_info.a4_color + obj_info.a4x3_color + obj_info.a4x4_color + obj_info.a4x5_color + obj_info.a4x6_color + obj_info.a4x7_color + obj_info.a4x8_color + obj_info.a4x9_color
        bad_lists = obj_info.other_pages
        # Переводим словарь с неправильными листами в json
        dict_temp_file_json = ast.literal_eval(bad_lists)
        len_bad_dict_temp = len(dict_temp_file_json)
    except Exception as e:
        print(e)
        color_pages = 0
        obj_info = None
        dict_temp_file_json = {}
        len_bad_dict_temp = 0

    content = {'obj': obj,
               'obj_info': obj_info,
               'bad_lists': dict_temp_file_json,
               'len_bad_dict_temp': len_bad_dict_temp,
               'color_pages': color_pages}

    return content


class GetInfoPrintTaskView(View):
    """
    Информация по конкретному заданию
    """

    def get(self, request):
        obj_id = int(request.GET.get('object'))  # Получаем id задачи из GET запроса
        content = get_task_info(obj_id)  # Получаем информацию по конкретному заданию
        return render(request, 'print_service_app/ajax/modal_details_task.html', content)

    def post(self, request):
        """
        Изменение статуса задачи сотрудником типографии
        """
        print(request.POST)
        emp = EmployeeModel.objects.get(user=request.user)
        print_task_id = request.POST['obj_id_for_change_status']  # Получаем id задачи, для которой меняем статус
        print_task_obj = PrintFilesModel.objects.get(id=print_task_id)  # Получаем объект модели с задачами
        print_task_obj.status = int(request.POST['TypeWorkTask_id'])  # Получаем код статуса
        print_task_obj.date_change_status = datetime.datetime.now()  # Устанавливаем дату и время изменения статуса
        print_task_obj.save()
        # Записываем в лог, создаем запись в таблице ChangeStatusHistoryModel
        save_status_log(print_task_id=print_task_id, print_task_status=print_task_obj.status, emp_id=emp.id)
        # Отправка письма через Celery
        if int(request.POST['TypeWorkTask_id']) == 3:
            # Если статус, что задача выполнена
            celery_email_print_done.delay(int(print_task_id))
        elif int(request.POST['TypeWorkTask_id']) == 0:
            # Если статус, что задача отменена
            print('Статус задачи', request.POST['TypeWorkTask_id'])
            celery_email_print_cancel.delay(int(print_task_id), request.POST['WhyCancel'])
        return HttpResponse(status=200)


class GetEditModalWindow(View):
    """ Редактирование задачи сотрудником типографии"""

    def get(self, request):
        """Загрузка модального окна редактирования задачи"""
        print(request.GET)
        obj_task = PrintFilesModel.objects.get(id=request.GET.get('obj_id'))  # Получение информации по задаче
        orders = OrdersModel.objects.get_queryset().order_by('order')  # Получение номеров заказов
        # Получение актуальных объектов
        objects = ObjectModel.objects.get_queryset().filter(show=True).order_by('object_name')
        marks = MarkDocModel.objects.get_queryset()  # Получение марок документации
        try:
            # Получение номеров договор в зависимости от выбранного объекта
            contracts = ContractModel.objects.get_queryset().filter(contract_object_id=obj_task.object.id).filter(
                show=True).order_by(
                'contract_name')
        except Exception as e:
            # Установка пустого поля в договора, если не выбран объект
            print(f'Контракт у {obj_task.id} не указан: {e}')  # Ошибка в консоль
            contracts = ContractModel.objects.get_queryset()
        content = {'objects': objects,
                   'orders': orders,
                   'obj': obj_task,
                   'contracts': contracts,
                   'marks': marks}
        return render(request, 'print_service_app/ajax/modal_edit_task.html', content)

    def post(self, request):
        """Сохранение изменений задачи"""
        print(f'GetEditModalWindow - request.POST: {request.POST}')
        # Получение редактируемой задачи
        task_obj = PrintFilesModel.objects.get(id=request.POST['obj_id'])
        # Установка новых значений
        task_obj.inventory_number_file = request.POST['input_inventory_number_file_value']
        task_obj.comment = request.POST['input_comment_value']
        task_obj.order_id = request.POST['order_id']
        task_obj.object_id = request.POST['object_id']
        task_obj.contract_id = request.POST['contract_id']
        task_obj.copy_count = request.POST['copy_count_value']
        task_obj.task_type_work = request.POST['TypeWorkTask_id']
        task_obj.print_folding = request.POST['folding_id']
        task_obj.color = request.POST['color_id']
        task_obj.mark_print_file_id = request.POST['mark_id']
        task_obj.save()
        return HttpResponse(status=200)


class GetEditListsModalWindow(View):
    """ Редактирование количества листов и форматов у задачи, сотрудником типографии"""

    def get(self, request):
        """Загрузка модального окна редактирования листов и форматов задачи"""
        print(request.GET)
        #  Получение задачи из бд
        obj_task = PrintFilesModel.objects.get(id=request.GET.get('obj_id'))
        lists_of_task = ListsFileModel.objects.get(print_file_id=obj_task.id)
        try:
            # Если есть не распознанные чб листы
            json_other_black_lists = ast.literal_eval(lists_of_task.other_pages)
            len_other_black_lists = len(json_other_black_lists)
        except Exception as e:
            print(e)
            len_other_black_lists = 0
            json_other_black_lists = ''

        try:
            # Если есть не распознанные цветные листы
            json_other_color_lists = ast.literal_eval(lists_of_task.other_pages_color)
            len_other_color_lists = len(json_other_color_lists)
        except Exception as e:
            print(e)
            json_other_color_lists = ''
            len_other_color_lists = ''

        content = {
            'obj': obj_task,
            'lists_of_task': lists_of_task,
            'other_black_lists': json_other_black_lists,
            'len_other_black_lists': len_other_black_lists,
            'other_color_lists': json_other_color_lists,
            'len_other_color_lists': len_other_color_lists}
        return render(request, 'print_service_app/ajax/modal_edit_lists_task.html', content)

    def post(self, request):
        """Сохранение изменений листов и форматов задачи"""
        print(f'request.POST: {request.POST}')
        task_obj = PrintFilesModel.objects.get(id=request.POST['obj_id'])
        task_lists = ListsFileModel.objects.get(print_file=task_obj)

        # Переводим request.post в словарь
        result_dict = dict(request.POST.lists())
        # Чистим от лишних ключей
        del result_dict['csrfmiddlewaretoken']
        del result_dict['obj_id']
        a4_count = 0  # Новый счетчик форматов А4

        # Обновляем листы согласно input-ам
        # Форматы А4
        task_lists.a4 = result_dict['input_a4'][0]
        del result_dict['input_a4']
        task_lists.a4_color = result_dict['input_a4_color'][0]
        del result_dict['input_a4_color']
        a4_count += 1 * (int(task_lists.a4) + int(task_lists.a4_color))

        # Форматы А3
        task_lists.a3 = result_dict['input_a3'][0]
        del result_dict['input_a3']
        task_lists.a3_color = result_dict['input_a3_color'][0]
        del result_dict['input_a3_color']
        a4_count += 2 * (int(task_lists.a3) + int(task_lists.a3_color))

        # Форматы А2
        task_lists.a2 = result_dict['input_a2'][0]
        del result_dict['input_a2']
        task_lists.a2_color = result_dict['input_a2_color'][0]
        del result_dict['input_a2_color']
        a4_count += 4 * (int(task_lists.a2) + int(task_lists.a2_color))

        # Форматы А1
        task_lists.a1 = result_dict['input_a1'][0]
        del result_dict['input_a1']
        task_lists.a1_color = result_dict['input_a1_color'][0]
        del result_dict['input_a1_color']
        a4_count += 8 * (int(task_lists.a1) + int(task_lists.a1_color))

        # Форматы А0
        task_lists.a0 = result_dict['input_a0'][0]
        del result_dict['input_a0']
        task_lists.a0_color = result_dict['input_a0_color'][0]
        del result_dict['input_a0_color']
        a4_count += 16 * (int(task_lists.a0) + int(task_lists.a0_color))

        # Форматы А4х3
        task_lists.a4x3 = result_dict['input_a4x3'][0]
        del result_dict['input_a4x3']
        task_lists.a4x3_color = result_dict['input_a4x3_color'][0]
        del result_dict['input_a4x3_color']
        a4_count += 3 * (int(task_lists.a4x3) + int(task_lists.a4x3_color))

        # Форматы А4х4
        task_lists.a4x4 = result_dict['input_a4x4'][0]
        del result_dict['input_a4x4']
        task_lists.a4x4_color = result_dict['input_a4x4_color'][0]
        del result_dict['input_a4x4_color']
        a4_count += 4 * (int(task_lists.a4x4) + int(task_lists.a4x4_color))

        # Форматы А4х5
        task_lists.a4x5 = result_dict['input_a4x5'][0]
        del result_dict['input_a4x5']
        task_lists.a4x5_color = result_dict['input_a4x5_color'][0]
        del result_dict['input_a4x5_color']
        a4_count += 5 * (int(task_lists.a4x5) + int(task_lists.a4x5_color))

        # Форматы А4х6
        task_lists.a4x6 = result_dict['input_a4x6'][0]
        del result_dict['input_a4x6']
        task_lists.a4x6_color = result_dict['input_a4x6_color'][0]
        del result_dict['input_a4x6_color']
        a4_count += 6 * (int(task_lists.a4x6) + int(task_lists.a4x6_color))

        # Форматы А4х7
        task_lists.a4x7 = result_dict['input_a4x7'][0]
        del result_dict['input_a4x7']
        task_lists.a4x7_color = result_dict['input_a4x7_color'][0]
        del result_dict['input_a4x7_color']
        a4_count += 7 * (int(task_lists.a4x7) + int(task_lists.a4x7_color))

        # Форматы А4х8
        task_lists.a4x8 = result_dict['input_a4x8'][0]
        del result_dict['input_a4x8']
        task_lists.a4x8_color = result_dict['input_a4x8_color'][0]
        del result_dict['input_a4x8_color']
        a4_count += 8 * (int(task_lists.a4x8) + int(task_lists.a4x8_color))

        # Форматы А4х9
        task_lists.a4x9 = result_dict['input_a4x9'][0]
        del result_dict['input_a4x9']
        task_lists.a4x9_color = result_dict['input_a4x9_color'][0]
        del result_dict['input_a4x9_color']
        a4_count += 9 * (int(task_lists.a4x9) + int(task_lists.a4x9_color))

        # Форматы А3х3
        task_lists.a3x3 = result_dict['input_a3x3'][0]
        del result_dict['input_a3x3']
        task_lists.a3x3_color = result_dict['input_a3x3_color'][0]
        del result_dict['input_a3x3_color']
        a4_count += 6 * (int(task_lists.a3x3) + int(task_lists.a3x3_color))

        # Форматы А3х4
        task_lists.a3x4 = result_dict['input_a3x4'][0]
        del result_dict['input_a3x4']
        task_lists.a3x4_color = result_dict['input_a3x4_color'][0]
        del result_dict['input_a3x4_color']
        a4_count += 8 * (int(task_lists.a3x4) + int(task_lists.a3x4_color))

        # Форматы А3х5
        task_lists.a3x5 = result_dict['input_a3x5'][0]
        del result_dict['input_a3x5']
        task_lists.a3x5_color = result_dict['input_a3x5_color'][0]
        del result_dict['input_a3x5_color']
        a4_count += 10 * (int(task_lists.a3x5) + int(task_lists.a3x5_color))

        # Форматы А3х6
        task_lists.a3x6 = result_dict['input_a3x6'][0]
        del result_dict['input_a3x6']
        task_lists.a3x6_color = result_dict['input_a3x6_color'][0]
        del result_dict['input_a3x6_color']
        a4_count += 12 * (int(task_lists.a3x6) + int(task_lists.a3x6_color))

        # Форматы А3х7
        task_lists.a3x7 = result_dict['input_a3x7'][0]
        del result_dict['input_a3x7']
        task_lists.a3x7_color = result_dict['input_a3x7_color'][0]
        del result_dict['input_a3x7_color']
        a4_count += 14 * (int(task_lists.a3x7) + int(task_lists.a3x7_color))

        # Форматы А2х3
        task_lists.a2x3 = result_dict['input_a2x3'][0]
        del result_dict['input_a2x3']
        task_lists.a2x3_color = result_dict['input_a2x3_color'][0]
        del result_dict['input_a2x3_color']
        a4_count += 12 * (int(task_lists.a2x3) + int(task_lists.a2x3_color))

        # Форматы А2х4
        task_lists.a2x4 = result_dict['input_a2x4'][0]
        del result_dict['input_a2x4']
        task_lists.a2x4_color = result_dict['input_a2x4_color'][0]
        del result_dict['input_a2x4_color']
        a4_count += 16 * (int(task_lists.a2x4) + int(task_lists.a2x4_color))

        # Форматы А2х5
        task_lists.a2x5 = result_dict['input_a2x5'][0]
        del result_dict['input_a2x5']
        task_lists.a2x5_color = result_dict['input_a2x5_color'][0]
        del result_dict['input_a2x5_color']
        a4_count += 20 * (int(task_lists.a2x5) + int(task_lists.a2x5_color))

        # Форматы А1х3
        task_lists.a1x3 = result_dict['input_a1x3'][0]
        del result_dict['input_a1x3']
        task_lists.a1x3_color = result_dict['input_a1x3_color'][0]
        del result_dict['input_a1x3_color']
        a4_count += 24 * (int(task_lists.a1x3) + int(task_lists.a1x3_color))

        # Форматы А1х4
        task_lists.a1x4 = result_dict['input_a1x4'][0]
        del result_dict['input_a1x4']
        task_lists.a1x4_color = result_dict['input_a1x4_color'][0]
        del result_dict['input_a1x4_color']
        a4_count += 32 * (int(task_lists.a1x4) + int(task_lists.a1x4_color))

        # Форматы А0х2
        task_lists.a0x2 = result_dict['input_a0x2'][0]
        del result_dict['input_a0x2']
        task_lists.a0x2_color = result_dict['input_a0x2_color'][0]
        del result_dict['input_a0x2_color']
        a4_count += 32 * (int(task_lists.a0x2) + int(task_lists.a0x2_color))

        # Форматы А0х3
        task_lists.a0x3 = result_dict['input_a0x3'][0]
        del result_dict['input_a0x3']
        task_lists.a0x3_color = result_dict['input_a0x3_color'][0]
        del result_dict['input_a0x3_color']
        a4_count += 48 * (int(task_lists.a0x3) + int(task_lists.a0x3_color))

        # Приводим словарь к виду, который в базе данных
        dict_to_other = {}
        for key, value in result_dict.items():
            if int(value[0]) > 0:
                dict_to_other[key] = int(value[0])
        task_lists.other_pages = dict_to_other
        task_lists.save()

        # Обновляем количество форматов а4
        task_obj.a4_count_formats = a4_count
        task_obj.save()

        # Печатаем в консоль для проверки данных
        print(task_obj)
        print(task_lists)
        print(result_dict)
        print(dict_to_other)

        return HttpResponse(status=200)


class GetInfoReportPrintTaskView(View):
    """Загрузка модального окна с кнопками загрузки отчетов по выбранной задаче"""

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
        # Если статус задания уже менялся, то при скачивании бланка ничего не менять,
        # в другом случае установить статус в работе
        if file_path_in_db.date_change_status is None:
            file_path_in_db.status = 2
            file_path_in_db.save()
            emp = EmployeeModel.objects.get(user=request.user)
            save_status_log(print_task_id=pk, print_task_status=file_path_in_db.status, emp_id=emp.id)
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_path_in_db.file_to_print))
        # Проверка на наличие файла в системе
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(file_path)
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=' + escape_uri_path(os.path.basename(file_path))
                return response
        raise Http404


class BlankPageView(View):
    """Страница загрузки бланка, для учета вручения документа сотрудниками типографии"""

    def get(self, request, pk):
        print_task = PrintFilesModel.objects.get(id=pk)
        pages_info = ListsFileModel.objects.get(print_file=print_task)
        # Считаем цветные листы
        color_pages = pages_info.a0_color + pages_info.a0x2_color + pages_info.a0x3_color + pages_info.a1_color + pages_info.a1x3_color + pages_info.a1x4_color + pages_info.a2_color + pages_info.a2x3_color + pages_info.a2x4_color + pages_info.a2x5_color + pages_info.a3_color + pages_info.a3x3_color + pages_info.a3x4_color + pages_info.a3x5_color + pages_info.a3x6_color + pages_info.a3x7_color + pages_info.a4_color + pages_info.a4x3_color + pages_info.a4x4_color + pages_info.a4x5_color + pages_info.a4x6_color + pages_info.a4x7_color + pages_info.a4x8_color + pages_info.a4x9_color
        # Формируем словарь с плохими листами
        bad_pages = ast.literal_eval(pages_info.other_pages)
        len_bad_pages = len(bad_pages)
        content = {'print_task': print_task,
                   'pages_info': pages_info,
                   'color_pages': color_pages,
                   'bad_pages': bad_pages,
                   'len_bad_pages': len_bad_pages}
        return render(request, 'print_service_app/blank_page.html', content)


class DownloadBlankView(View):
    """Скачивание заявки на печать
    Более не актуально"""

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
            # Получение всего списка задач, отсортированного от нового к старым
            all_tasks_in_project = PrintFilesModel.objects.get_queryset().order_by('-id')
            len_all_tasks = len(all_tasks_in_project)
            content = {'len_all_tasks': len_all_tasks,
                       "user_permission": user_permission}
            return render(request, 'print_service_app/all-print-task.html', content)
        else:
            content = {}
            return render(request, 'print_service_app/permission-error.html', content)


def get_all_task(request):
    """Функция для ajax запроса получения списка актуальных задач в реальном времени"""
    print(request.GET)
    now_value = int(request.GET.get('now_value'))
    all_tasks_in_project = PrintFilesModel.objects.order_by('-id')
    all_tasks = all_tasks_in_project[:now_value]
    content = {"all_tasks": all_tasks
               }
    return render(request, 'print_service_app/ajax/all-tasks-table.html', content)


class ReportView(View):
    """Страница для формирования отчетов"""

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
        """Получение дат для сортировки заданий в определенном временном промежутке"""
        print(f'request.POST: {request.POST}')
        # Проверка установлена ли начальная дата, если нет, устанавливаем 01.01.1990
        try:
            start_date = datetime.datetime.strptime(request.POST.get('date_start'), "%Y-%m-%d").date()
        except Exception as e:
            print(f'{e}. Начальная дата для отчета не задана. Автоматически установлена 01.01.1990')
            start_date = datetime.date(1990, 1, 1)
        # Проверка установлена ли конечная дата, если нет, устанавливаем сегодняшнюю дату
        try:
            end_date = datetime.datetime.strptime(request.POST.get('date_end'), "%Y-%m-%d").date()
        except Exception as e:
            end_date = datetime.datetime.now().date()
            print(f'{e}. Конечная дата для отчета не задана. Автоматически установлена {end_date}')
        print_end_date = copy(end_date)
        end_date += datetime.timedelta(days=1)  # Прибавляем к конечно дате еще один день
        print(f'Запрошен отчет на даты: {start_date} - {end_date}')
        search_result = PrintFilesModel.objects.get_queryset()  # Получаем queryset со всеми заданиями
        if start_date:
            # Если есть начальная дата, фильтруем от начальной включительно
            search_result = search_result.filter(add_file_date__gte=start_date)
            print(search_result)
        if end_date:
            # Если есть конечная дата, фильтруем до конечной включительно
            search_result = search_result.filter(add_file_date__lte=end_date)
            print(search_result)
        # Фильтруем задачи со статусом готово и сортируем от новых к старым
        search_result = search_result.filter(status=3).order_by('-id')
        content = {'search_result': search_result,
                   'start_date': f'{start_date.strftime("%d.%m.%Y")}',
                   'end_date': f'{print_end_date.strftime("%d.%m.%Y")}'}
        # return HttpResponse(status=200)
        return render(request, 'print_service_app/ajax/result-report.html', content)


class GeneratePrintReportTableView(View):
    """Отчет Print(по выводу) для одной задачи"""

    def get(self, request, pk):
        tasks = PrintFilesModel.objects.get_queryset().filter(id=pk)
        if get_print_report_xls(tasks):
            # Если формирование файла прошло без ошибок
            file_path_to_export = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx',
                                               'export_print.xlsx')
            if os.path.exists(file_path_to_export):
                # Если файл существует (сохранился)
                with open(file_path_to_export, 'rb') as fh:
                    # Установка mimetype для правильной обработки браузером
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    response = HttpResponse(fh.read(), content_type=mime_type)
                    # В названии файла устанавливаем номер задачи с пометкой print
                    response['Content-Disposition'] = 'attachment; filename=' + escape_uri_path(
                        f'{PrintFilesModel.objects.get(id=pk).inventory_number_request}-print.xlsx')
                    return response
            raise Http404
        else:
            return Http404


class GeneratePrintReportListTableView(View):
    """Формирования отчета print(по выводу) по промежутку дат"""

    def get(self, request):

        try:
            start_date = datetime.datetime.strptime(request.GET['date-start'], "%Y-%m-%d").date()

        except Exception as e:
            print(f'{e}. Начальная дата для отчета не задана. Автоматически установлена 01.01.1990')
            start_date = datetime.date(1990, 1, 1)
        try:
            end_date = datetime.datetime.strptime(request.GET['date-end'], "%Y-%m-%d").date()
        except Exception as e:
            end_date = datetime.datetime.now().date()
            print(f'{e}. Конечная дата для отчета не задана. Автоматически установлена {end_date}')
        end_date += datetime.timedelta(days=1)
        print(f'Запрошен xls отчет на даты: {start_date} - {end_date}')
        search_result = PrintFilesModel.objects.get_queryset().filter(status=3)
        if start_date:
            search_result = search_result.filter(add_file_date__gte=start_date)
        if end_date:
            search_result = search_result.filter(add_file_date__lte=end_date)
        if get_print_report_xls(search_result):
            return HttpResponse(status=200)
        else:
            return Http404


class GenerateDispatcherReportTableView(View):
    """Диспетчерский (по заявкам) файл по одной задаче"""

    def get(self, request, pk):
        print(request.GET)
        tasks = PrintFilesModel.objects.get_queryset().filter(id=pk)
        if get_dispatcher_report_xls(tasks):
            file_path_to_export = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx',
                                               'export_dispatcher.xlsx')
            if os.path.exists(file_path_to_export):
                with open(file_path_to_export, 'rb') as fh:
                    # Установка mimetype для правильной обработки браузером
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    response = HttpResponse(fh.read(), content_type=mime_type)
                    # В названии файла устанавливаем номер задачи с пометкой dispatcher
                    response['Content-Disposition'] = 'attachment; filename=' + escape_uri_path(
                        f'{PrintFilesModel.objects.get(id=pk).inventory_number_request}-dispatcher.xlsx')
                    return response
            raise Http404
        else:
            return Http404


class GenerateDispatcherReportListTableView(View):
    """Формирование диспетчерского файл (по заявкам) по нескольким задачам"""

    def get(self, request):
        try:
            start_date = datetime.datetime.strptime(request.GET['date-start'], "%Y-%m-%d").date()
        except Exception as e:
            print(f'{e}. Начальная дата для отчета не задана. Автоматически установлена 01.01.1990')
            start_date = datetime.date(1990, 1, 1)
        try:
            end_date = datetime.datetime.strptime(request.GET['date-end'], "%Y-%m-%d").date()
        except Exception as e:
            end_date = datetime.datetime.now().date()
            print(f'{e}. Конечная дата для отчета не задана. Автоматически установлена {end_date}')
        end_date += datetime.timedelta(days=1)
        print(f'Запрошен xls отчет на даты: {start_date} - {end_date}')
        search_result = PrintFilesModel.objects.get_queryset().filter(status=3)
        if start_date:
            search_result = search_result.filter(add_file_date__gte=start_date)
        if end_date:
            search_result = search_result.filter(add_file_date__lte=end_date)
        # Формируем диспетчерский отчет из полученного списка задач
        if get_dispatcher_report_xls(search_result):
            return HttpResponse(status=200)
        else:
            return Http404


class DownloadExportReportView(View):
    """Скачивание экспорта итогового файла Print (по выводы) для промежутка дат"""

    def get(self, request):
        print("Сейчас тут")
        file_path_to_export = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx',
                                           'export_print.xlsx')
        if os.path.exists(file_path_to_export):
            with open(file_path_to_export, 'rb') as fh:
                # Установка mimetype для правильной обработки браузером
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=' + escape_uri_path(f'export_print.xlsx')
                return response
        raise Http404


class DownloadDispatcherExportReportView(View):
    """Скачивание экспорта итогового файла Dispatcher (по заявкам) для промежутка дат"""

    def get(self, request):
        file_path_to_export = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx',
                                           'export_dispatcher.xlsx')
        if os.path.exists(file_path_to_export):
            with open(file_path_to_export, 'rb') as fh:
                # Установка mimetype для правильной обработки браузером
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=' + escape_uri_path(f'export_dispatcher.xlsx')
                return response
        raise Http404
