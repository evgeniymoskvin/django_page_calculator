import os

import openpyxl

from django.conf import settings

from page_calculator_app.models import PrintFilesModel, EmployeeModel, ListsFileModel, ChangeStatusHistoryModel, \
    CpeModel


def get_print_report_xls(objects_tasks: list):
    """
    Формирование отчета Print
    """
    file_xlsx_path = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx', 'GurnRas_Print&Scan.xlsx')
    file_path_to_export = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx', 'export_print.xlsx')
    wb = openpyxl.load_workbook(filename=file_xlsx_path, data_only=True)
    page = wb.active
    for task in objects_tasks:
        try:
            pages_info_task = ListsFileModel.objects.get(print_file=task)
        except:
            pages_info_task = ListsFileModel()
        try:
            task_history = ChangeStatusHistoryModel.objects.all().filter(print_task=task)
            last_recording_done = task_history.filter(status=3).last()
            date_last = last_recording_done.date_change_status
            date_change_status_to_done = date_last.strftime('%d.%m.%Y')
            who_change_status_to_done = f'{last_recording_done.emp.last_name} {last_recording_done.emp.first_name[:1]}. {last_recording_done.emp.middle_name[:1]}.'
        except Exception as e:
            print(f'Get last history error: {e}')
            date_change_status_to_done = ''
            who_change_status_to_done = ''
        row = ['',  # № п/п
               date_change_status_to_done,  # Дата выполнения
               '',  # Инв. № тома Элерон
               task.inventory_number_file,  # Инв. № тома
               task.inventory_number_request,  # Номер заявки
               task.add_file_date.date().strftime('%d.%m.%Y'),  # Дата заявки
               task.copy_count,  # Печать
               '',  # Скан
               '',  # Наклейка А4
               '',  # Наклейка А5
               # A4
               pages_info_task.a4 * task.copy_count,  # А4
               '',  # Скан
               pages_info_task.a4 * task.copy_count,  # Всего
               pages_info_task.a4_color * task.copy_count,  # A4 цвет
               '',  # Скан
               pages_info_task.a4_color * task.copy_count,  # А4 цвет всего
               # A3
               pages_info_task.a3 * task.copy_count,  # A3
               '',  # Скан
               pages_info_task.a3 * task.copy_count,  # Всего
               pages_info_task.a3_color * task.copy_count,  # А3 цвет
               '',  # Скан
               pages_info_task.a3_color * task.copy_count,  # А3 цвет всего
               # A2
               pages_info_task.a2 * task.copy_count,  # А2
               '',  # Скан
               pages_info_task.a2 * task.copy_count,  # A2 всего
               pages_info_task.a2_color * task.copy_count,  # А2 цвет
               '',  # Скан
               pages_info_task.a2_color * task.copy_count,  # A2 цвет всего
               # A1
               pages_info_task.a1 * task.copy_count,  # a1
               '',  # Скан
               pages_info_task.a1 * task.copy_count,  # a1 всего
               pages_info_task.a1_color * task.copy_count,  # a1 цветной
               '',  # Скан
               pages_info_task.a1_color * task.copy_count,  # a1 цветной всего
               # A0
               pages_info_task.a0 * task.copy_count,  # a0
               '',  # Скан
               pages_info_task.a0 * task.copy_count,  # a0 всего
               pages_info_task.a0_color * task.copy_count,  # a0 цветной
               '',  # Скан
               pages_info_task.a0_color * task.copy_count,  # а0 цветной всего
               # A4x3
               pages_info_task.a4x3 * task.copy_count,  # A4x3
               '',  # Скан
               pages_info_task.a4x3 * task.copy_count,  # A4x3 всего
               pages_info_task.a4x3_color * task.copy_count,  # A4x3 цветной
               '',  # Скан
               pages_info_task.a4x3_color * task.copy_count,  # a4x3 цветной всего
               # A4x4
               pages_info_task.a4x4 * task.copy_count,
               '',  # Скан
               pages_info_task.a4x4 * task.copy_count,
               pages_info_task.a4x4_color * task.copy_count,
               '',  # Скан
               pages_info_task.a4x4_color * task.copy_count,
               # A4x5
               pages_info_task.a4x5 * task.copy_count,
               '',  # Скан
               pages_info_task.a4x5 * task.copy_count,
               pages_info_task.a4x5_color * task.copy_count,
               '',  # Скан
               pages_info_task.a4x5_color * task.copy_count,
               # A4x6
               pages_info_task.a4x6 * task.copy_count,
               '',  # Скан
               pages_info_task.a4x6 * task.copy_count,
               pages_info_task.a4x6_color * task.copy_count,
               '',  # Скан
               pages_info_task.a4x6_color * task.copy_count,
               # A4x7
               pages_info_task.a4x7 * task.copy_count,
               '',  # Скан
               pages_info_task.a4x7 * task.copy_count,
               pages_info_task.a4x7_color * task.copy_count,
               '',  # Скан
               pages_info_task.a4x7_color * task.copy_count,
               # A4x8
               pages_info_task.a4x8 * task.copy_count,
               '',  # Скан
               pages_info_task.a4x8 * task.copy_count,
               pages_info_task.a4x8_color * task.copy_count,
               '',  # Скан
               pages_info_task.a4x8_color * task.copy_count,
               # A4x9
               pages_info_task.a4x9 * task.copy_count,
               '',  # Скан
               pages_info_task.a4x9 * task.copy_count,
               pages_info_task.a4x9_color * task.copy_count,
               '',  # Скан
               pages_info_task.a4x9_color * task.copy_count,
               # A3x3
               pages_info_task.a3x3 * task.copy_count,
               '',  # Скан
               pages_info_task.a3x3 * task.copy_count,
               pages_info_task.a3x3_color * task.copy_count,
               '',  # Скан
               pages_info_task.a3x3_color * task.copy_count,
               # A3x4
               pages_info_task.a3x4 * task.copy_count,
               '',  # Скан
               pages_info_task.a3x4 * task.copy_count,
               pages_info_task.a3x4_color * task.copy_count,
               '',  # Скан
               pages_info_task.a3x4_color * task.copy_count,
               # A3x5
               pages_info_task.a3x5 * task.copy_count,
               '',  # Скан
               pages_info_task.a3x5 * task.copy_count,
               pages_info_task.a3x5_color * task.copy_count,
               '',  # Скан
               pages_info_task.a3x5_color * task.copy_count,
               # A3x6
               pages_info_task.a3x6 * task.copy_count,
               '',  # Скан
               pages_info_task.a3x6 * task.copy_count,
               pages_info_task.a3x6_color * task.copy_count,
               '',  # Скан
               pages_info_task.a3x6_color * task.copy_count,
               # A3x7
               pages_info_task.a3x7 * task.copy_count,
               '',  # Скан
               pages_info_task.a3x7 * task.copy_count,
               pages_info_task.a3x7_color * task.copy_count,
               '',  # Скан
               pages_info_task.a3x7_color * task.copy_count,
               # A2x3
               pages_info_task.a2x3 * task.copy_count,
               '',  # Скан
               pages_info_task.a2x3 * task.copy_count,
               pages_info_task.a2x3_color * task.copy_count,
               '',  # Скан
               pages_info_task.a2x3_color * task.copy_count,
               # A2x4
               pages_info_task.a2x4 * task.copy_count,
               '',  # Скан
               pages_info_task.a2x4 * task.copy_count,
               pages_info_task.a2x4_color * task.copy_count,
               '',  # Скан
               pages_info_task.a2x4_color * task.copy_count,
               # A2x5
               pages_info_task.a2x5 * task.copy_count,
               '',  # Скан
               pages_info_task.a2x5 * task.copy_count,
               pages_info_task.a2x5_color * task.copy_count,
               '',  # Скан
               pages_info_task.a2x5_color * task.copy_count,
               # A1x3
               pages_info_task.a1x3 * task.copy_count,
               '',  # Скан
               pages_info_task.a1x3 * task.copy_count,
               pages_info_task.a1x3_color * task.copy_count,
               '',  # Скан
               pages_info_task.a1x3_color * task.copy_count,
               # A1x4
               pages_info_task.a1x4 * task.copy_count,
               '',  # Скан
               pages_info_task.a1x4 * task.copy_count,
               pages_info_task.a1x4_color * task.copy_count,
               '',  # Скан
               pages_info_task.a1x4_color * task.copy_count,
               # A0x2
               pages_info_task.a0x2 * task.copy_count,
               '',  # Скан
               pages_info_task.a0x2 * task.copy_count,
               pages_info_task.a0x2_color * task.copy_count,
               '',  # Скан
               pages_info_task.a0x2_color * task.copy_count,
               # A0x3
               pages_info_task.a0x3 * task.copy_count,
               '',  # Скан
               pages_info_task.a0x3 * task.copy_count,
               pages_info_task.a0x3_color * task.copy_count,
               '',  # Скан
               pages_info_task.a0x3_color * task.copy_count,
               who_change_status_to_done
               ]
        page.append(row)
    try:
        wb.save(filename=file_path_to_export)
        print(f'Файл сохранен')
        return True
    except Exception as e:
        return False


def get_dispatcher_report_xls(objects_tasks: list):
    """
    Формирование диспетчерского отчета
    """
    file_xlsx_path = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx', 'dispatcher_blank.xlsx')
    file_path_to_export = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx', 'export_dispatcher.xlsx')
    wb = openpyxl.load_workbook(filename=file_xlsx_path, data_only=True)
    page = wb.active
    for task in objects_tasks:
        try:
            # task= PrintFilesModel()
            task_history = ChangeStatusHistoryModel.objects.all().filter(print_task=task)
            last_recording_done = task_history.filter(status=3).last()
            date_last = last_recording_done.date_change_status
            date_change_status_to_done = date_last.strftime('%d.%m.%Y')
            who_change_status_to_done = f'{last_recording_done.emp.last_name} {last_recording_done.emp.first_name[:1]}. {last_recording_done.emp.middle_name[:1]}.'
        except Exception as e:
            print(f'Get last history error: {e}')
            date_change_status_to_done = ''
            who_change_status_to_done = ''
        inventory_name = task.inventory_number_file.split('И')[0]

        try:
            correction_number = f'И{task.inventory_number_file.split("И")[1]}'
        except Exception as e:
            print(f'Номер изменения в названии альбома не найден: {e}')
            correction_number = ''

        try:
            cpe_task = CpeModel.objects.get_queryset().filter(cpe_object=task.object).filter(cpe_important=True)[
                0].cpe_user.last_name
        except Exception as e:
            print(f'Не удалось определить ГИП-а: {e}')
            cpe_task = ''

        try:
            contract_name = task.contract.contract_name
        except Exception as e:
            print(f'Не удалось определить договор: {e}')
            contract_name = ''

        try:
            task_order = task.order.order
            task_order_name = task.order.order_name
        except Exception as e:
            print(f'Не удалось определить заказчика: {e}')
            task_order = ''
            task_order_name = ''

        try:
            object_code = task.object.object_code
        except Exception as e:
            print(f'Не удалось определить код объекта: {e}')
            object_code = ''

        try:
            mark_doc = task.mark_print_file.mark_doc
        except Exception as e:
            print(f'Не удалось определить марку документа: {e}')
            mark_doc = ''

        if task.task_type_work == 0:
            task_type_work = '-'
        elif task.task_type_work == 1:
            task_type_work = 'РД'
        elif task.task_type_work == 2:
            task_type_work = 'ПД'
        elif task.task_type_work == 3:
            task_type_work = 'ОБИН'
        elif task.task_type_work == 4:
            task_type_work = 'НИОКР'
        else:
            task_type_work = ''

        row = [
            task.inventory_number_request,  # Номер заявки
            task.add_file_date.strftime('%d.%m.%Y'),  # Дата приема
            inventory_name,  # Инв номер альбома ...
            correction_number,  # Номер корректировки
            '',  # Инв. № альбома ...
            task_type_work,  # Марка документации
            mark_doc,  # Раздел проекта
            task.emp_upload_file.department_group.group_dep_abr,  # Управление
            contract_name,  # Договор
            task_order,  # код заказчика
            object_code,  # Код объекта
            task_order_name,  # заказчик
            cpe_task,  # ГИП
            task.emp_upload_file.last_name,  # Исполнитель
            task.emp_upload_file.user_phone,  # Телефон
            task.count_pages,  # Объем работы, лист
            '',  # Тираж, шт.
            '',  # Скан
            task.copy_count,  # Печать шт.
            '',  # Диск
            '',  # Заказчик, шт
            '',  # Архив, шт
            '',  # Отдел, шт.
            date_change_status_to_done,  # Дата готовности
            '',  # Дата выдачи
            '',  # Примечание
        ]
        page.append(row)
    try:
        wb.save(filename=file_path_to_export)
        return True
    except Exception as e:
        print(f'Файл не сохранен: {e}')
        return False
