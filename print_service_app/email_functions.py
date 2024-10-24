import os
import time
from django.core.mail import EmailMessage
from page_calculator_app.models import PrintFilesModel


def task_print_done(print_task_id):
    """Отправка сообщения о готовности печати"""
    print_task = PrintFilesModel.objects.get(id=print_task_id)
    print_task_name = print_task.inventory_number_request
    email_author = EmailMessage(f'Задание на печать {print_task_name} выполнено',
                                f'Задание на печать {print_task_name} выполнено',
                                to=[print_task.emp_upload_file.user.email])
    try:
        email_author.send()
        print(
            f'Письмо по заданию {print_task_name} отправлено {print_task.emp_upload_file}: {print_task.emp_upload_file.user.email}')
    except Exception as e:
        print(f'Error send email: {e}')


def task_print_cancel(print_task_id, text_cancel):
    """Отправка сообщения об отмене печати"""
    print_task = PrintFilesModel.objects.get(id=print_task_id)
    print_task_name = print_task.inventory_number_request
    email_author = EmailMessage(f'Задание на печать {print_task_name} отменено',
                                f'Задание на печать {print_task_name} отменено. Причина: {text_cancel}',
                                to=[print_task.emp_upload_file.user.email])
    try:
        email_author.send()
        print(
            f'Письмо отмены задания {print_task_name} отправлено {print_task.emp_upload_file}: {print_task.emp_upload_file.user.email}')
    except Exception as e:
        print(f'Error send email: {e}')
