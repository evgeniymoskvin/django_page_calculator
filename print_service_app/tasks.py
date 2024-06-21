import datetime
import os
from django.conf import settings
from django.db.models import Q
from django.core.mail import EmailMessage

from page_calculator_app.models import PrintFilesModel

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


