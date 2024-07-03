import os

import openpyxl

from django.conf import settings

from page_calculator_app.models import PrintFilesModel, EmployeeModel, ListsFileModel, ChangeStatusHistoryModel


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
               pages_info_task.a4,  # А4
               '',  # Скан
               pages_info_task.a4,  # Всего
               pages_info_task.a4_color,  # A4 цвет
               '',  # Скан
               pages_info_task.a4_color,  # А4 цвет всего
               # A3
               pages_info_task.a3,  # A3
               '',  # Скан
               pages_info_task.a3,  # Всего
               pages_info_task.a3_color,  # А3 цвет
               '',  # Скан
               pages_info_task.a3_color,  # А3 цвет всего
               # A2
               pages_info_task.a2,  # А2
               '',  # Скан
               pages_info_task.a2,  # A2 всего
               pages_info_task.a2_color,  # А2 цвет
               '',  # Скан
               pages_info_task.a2_color,  # A2 цвет всего
               # A1
               pages_info_task.a1,  # a1
               '',  # Скан
               pages_info_task.a1,  # a1 всего
               pages_info_task.a1_color,  # a1 цветной
               '',  # Скан
               pages_info_task.a1_color,  # a1 цветной всего
               # A0
               pages_info_task.a0,  # a0
               '',  # Скан
               pages_info_task.a0,  # a0 всего
               pages_info_task.a0_color,  # a0 цветной
               '',  # Скан
               pages_info_task.a0_color,  # а0 цветной всего
               # A4x3
               pages_info_task.a4x3,  # A4x3
               '',  # Скан
               pages_info_task.a4x3,  # A4x3 всего
               pages_info_task.a4x3_color,  # A4x3 цветной
               '',  # Скан
               pages_info_task.a4x3_color,  # a4x3 цветной всего
               # A4x4
               pages_info_task.a4x4,
               '',  # Скан
               pages_info_task.a4x4,
               pages_info_task.a4x4_color,
               '',  # Скан
               pages_info_task.a4x4_color,
               # A4x5
               pages_info_task.a4x5,
               '',  # Скан
               pages_info_task.a4x5,
               pages_info_task.a4x5_color,
               '',  # Скан
               pages_info_task.a4x5_color,
               # A4x6
               pages_info_task.a4x6,
               '',  # Скан
               pages_info_task.a4x6,
               pages_info_task.a4x6_color,
               '',  # Скан
               pages_info_task.a4x6_color,
               # A4x7
               pages_info_task.a4x7,
               '',  # Скан
               pages_info_task.a4x7,
               pages_info_task.a4x7_color,
               '',  # Скан
               pages_info_task.a4x7_color,
               # A4x8
               pages_info_task.a4x8,
               '',  # Скан
               pages_info_task.a4x8,
               pages_info_task.a4x8_color,
               '',  # Скан
               pages_info_task.a4x8_color,
               # A4x9
               pages_info_task.a4x9,
               '',  # Скан
               pages_info_task.a4x9,
               pages_info_task.a4x9_color,
               '',  # Скан
               pages_info_task.a4x9_color,
               # A3x3
               pages_info_task.a3x3,
               '',  # Скан
               pages_info_task.a3x3,
               pages_info_task.a3x3_color,
               '',  # Скан
               pages_info_task.a3x3_color,
               # A3x4
               pages_info_task.a3x4,
               '',  # Скан
               pages_info_task.a3x4,
               pages_info_task.a3x4_color,
               '',  # Скан
               pages_info_task.a3x4_color,
               # A3x5
               pages_info_task.a3x5,
               '',  # Скан
               pages_info_task.a3x5,
               pages_info_task.a3x5_color,
               '',  # Скан
               pages_info_task.a3x5_color,
               # A3x6
               pages_info_task.a3x6,
               '',  # Скан
               pages_info_task.a3x6,
               pages_info_task.a3x6_color,
               '',  # Скан
               pages_info_task.a3x6_color,
               # A3x7
               pages_info_task.a3x7,
               '',  # Скан
               pages_info_task.a3x7,
               pages_info_task.a3x7_color,
               '',  # Скан
               pages_info_task.a3x7_color,
               # A2x3
               pages_info_task.a2x3,
               '',  # Скан
               pages_info_task.a2x3,
               pages_info_task.a2x3_color,
               '',  # Скан
               pages_info_task.a2x3_color,
               # A2x4
               pages_info_task.a2x4,
               '',  # Скан
               pages_info_task.a2x4,
               pages_info_task.a2x4_color,
               '',  # Скан
               pages_info_task.a2x4_color,
               # A2x5
               pages_info_task.a2x5,
               '',  # Скан
               pages_info_task.a2x5,
               pages_info_task.a2x5_color,
               '',  # Скан
               pages_info_task.a2x5_color,
               # A1x3
               pages_info_task.a1x3,
               '',  # Скан
               pages_info_task.a1x3,
               pages_info_task.a1x3_color,
               '',  # Скан
               pages_info_task.a1x3_color,
               # A1x4
               pages_info_task.a1x4,
               '',  # Скан
               pages_info_task.a1x4,
               pages_info_task.a1x4_color,
               '',  # Скан
               pages_info_task.a1x4_color,
               # A0x2
               pages_info_task.a0x2,
               '',  # Скан
               pages_info_task.a0x2,
               pages_info_task.a0x2_color,
               '',  # Скан
               pages_info_task.a0x2_color,
               # A0x3
               pages_info_task.a0x3,
               '',  # Скан
               pages_info_task.a0x3,
               pages_info_task.a0x3_color,
               '',  # Скан
               pages_info_task.a0x3_color,
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
    file_xlsx_path = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx', 'GurnRas_Print&Scan.xlsx')
    file_path_to_export = os.path.join(settings.BASE_DIR, 'print_service_app', 'xlsx', 'export_print.xlsx')
    pass
