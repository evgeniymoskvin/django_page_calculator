import datetime
import os
import time
from django.conf import settings
from django.db.models import Q
from django.core.mail import EmailMessage
from PIL import Image, ImageStat
from pdf2image import convert_from_path



from page_calculator_app.models import PrintFilesModel, ListsFileModel

from django_page_calculator.celery import app

from .email_functions import task_print_done





@app.task()
def delete_files():
    """
    Удаление файлов из хранилища и базы данных спустя 7 дней для заданий со статусом 'Аннулировано' и 'Готов'
    """
    today = datetime.datetime.today()
    count_tasks = 0
    count_delete_tasks_files = 0
    all_print_tasks = PrintFilesModel.objects.get_queryset().filter(Q(status=3) | Q(status=0))
    for task in all_print_tasks:
        task_date = task.date_change_status.date()
        task_date_delta = (today - task_date).days
        count_tasks += 1
        if task_date_delta > 7:
            count_delete_tasks_files += 1
            file_path = os.path.join(settings.MEDIA_ROOT, str(task.file_to_print))
            if os.path.exists(file_path):
                os.remove(file_path)
            task.file_to_print = None
            task.save()
    return f'Всего обработано записей {count_tasks}. Удалено файлов: {count_delete_tasks_files}'


@app.task()
def celery_email_print_done(task_done_id):
    task_print_done(task_done_id)
    return f'Печать id={task_done_id} выполнена. Письмо отправлено.'


@app.task()
def celery_check_color_pages(file_path, all_lists_file, lists_file_id):
    start_time = time.time()
    lists_file = ListsFileModel.objects.get(id=lists_file_id)
    print(f'Определение чб и цветного для {lists_file.print_file.inventory_number_request}')
    # Для windows
    pages = convert_from_path(file_path, 50, fmt='jpeg', poppler_path=r'C:\Program Files\poppler-24.02.0\Library\bin')
    # Для linux
    # pages = convert_from_path(file_path, 50, fmt='jpeg')
    to_jpeg_time = time.time() - start_time
    print(f"Разбиралось на jpeg: {to_jpeg_time} секунд")

    for count, page in enumerate(pages):
        result_check_color = detect_color_image(page)
        print(f'Лист {count+1} - result_check_color: {result_check_color}')
        if result_check_color is True:
            if all_lists_file[count][2] == 'A0':
                lists_file.a0 -= 1
                lists_file.a0_color += 1
            elif all_lists_file[count][2] == 'A0x2':
                lists_file.a0x2 -= 1
                lists_file.a0x2_color += 1
            elif all_lists_file[count][2] == 'A0x3':
                lists_file.a0x3 -= 1
                lists_file.a0x3_color += 1
            elif all_lists_file[count][2] == 'A1':
                lists_file.a1 -= 1
                lists_file.a1_color += 1
            elif all_lists_file[count][2] == 'A1x3':
                lists_file.a1x3 -= 1
                lists_file.a1x3_color += 1
            elif all_lists_file[count][2] == 'A1x4':
                lists_file.a1x4 -= 1
                lists_file.a1x4_color += 1
            elif all_lists_file[count][2] == 'A1x4':
                lists_file.a1x4 -= 1
                lists_file.a1x4_color += 1
            elif all_lists_file[count][2] == 'A2':
                lists_file.a2 -= 1
                lists_file.a2_color += 1
            elif all_lists_file[count][2] == 'A2x3':
                lists_file.a2x3 -= 1
                lists_file.a2x3_color += 1
            elif all_lists_file[count][2] == 'A2x4':
                lists_file.a2x4 -= 1
                lists_file.a2x4_color += 1
            elif all_lists_file[count][2] == 'A2x5':
                lists_file.a2x5 -= 1
                lists_file.a2x5_color += 1
            elif all_lists_file[count][2] == 'A3':
                lists_file.a3 -= 1
                lists_file.a3_color += 1
            elif all_lists_file[count][2] == 'A3x3':
                lists_file.a3x3 -= 1
                lists_file.a3x3_color += 1
            elif all_lists_file[count][2] == 'A3x4':
                lists_file.a3x4 -= 1
                lists_file.a3x4_color += 1
            elif all_lists_file[count][2] == 'A3x5':
                lists_file.a3x5 -= 1
                lists_file.a3x5_color += 1
            elif all_lists_file[count][2] == 'A3x6':
                lists_file.a3x6 -= 1
                lists_file.a3x6_color += 1
            elif all_lists_file[count][2] == 'A3x7':
                lists_file.a3x7 -= 1
                lists_file.a3x7_color += 1
            elif all_lists_file[count][2] == 'A4':
                lists_file.a4 -= 1
                lists_file.a4_color += 1
            elif all_lists_file[count][2] == 'A4x3':
                lists_file.a4x3 -= 1
                lists_file.a4x3_color += 1
            elif all_lists_file[count][2] == 'A4x4':
                lists_file.a4x4 -= 1
                lists_file.a4x4_color += 1
            elif all_lists_file[count][2] == 'A4x5':
                lists_file.a4x5 -= 1
                lists_file.a4x5_color += 1
            elif all_lists_file[count][2] == 'A4x6':
                lists_file.a4x6 -= 1
                lists_file.a4x6_color += 1
            elif all_lists_file[count][2] == 'A4x7':
                lists_file.a4x7 -= 1
                lists_file.a4x7_color += 1
            elif all_lists_file[count][2] == 'A4x8':
                lists_file.a4x8 -= 1
                lists_file.a4x8_color += 1
            elif all_lists_file[count][2] == 'A4x9':
                lists_file.a4x9 -= 1
                lists_file.a4x9_color += 1

    lists_file.save()
    return f"Разобрали на цветные и чб за {time.time()-start_time} секунд"


def detect_color_image(file, thumb_size=40, MSE_cutoff=1, adjust_color_bias=True):
    """
    Определение цветных и чб листов
    """
    pil_img = file
    bands = pil_img.getbands()
    if bands == ('R', 'G', 'B') or bands == ('R', 'G', 'B', 'A'):
        thumb = pil_img.resize((thumb_size, thumb_size))
        SSE, bias = 0, [0, 0, 0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias) / 3 for b in bias]
        for pixel in thumb.getdata():
            mu = sum(pixel) / 3
            SSE += sum((pixel[i] - mu - bias[i]) * (pixel[i] - mu - bias[i]) for i in [0, 1, 2])
        MSE = float(SSE) / (thumb_size * thumb_size)
        if MSE <= MSE_cutoff:
            print("grayscale\t", )
            return "Grayscale"
        else:
            print("Color\t\t\t", )
            return True
    elif len(bands) == 1:
        print("Black and white", bands)
        return True
    else:
        print("Don't know...", bands)
        return 'dont_know'
