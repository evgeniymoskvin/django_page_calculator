from django import template
from ..models import *

register = template.Library()


@register.simple_tag()
def get_name(user):
    full_user = EmployeeModel.objects.get(user=user)
    return full_user


@register.simple_tag()
def get_short_name(user):
    full_user = EmployeeModel.objects.get(user=user)
    return f'{full_user.last_name} {full_user.first_name[:1]}.{full_user.middle_name[:1]}'


@register.simple_tag()
def get_who_change_status_in_work(id_task):
    try:
        tasks = ChangeStatusHistoryModel.objects.all().filter(print_task_id=id_task)
        first_recording_in_work = tasks.filter(status=2).first().emp
        return first_recording_in_work
    except:
        return f'Данные отсутствуют'


@register.simple_tag()
def get_when_change_status_in_work(id_task):
    try:
        tasks = ChangeStatusHistoryModel.objects.all().filter(print_task_id=id_task)
        first_recording_in_work = tasks.filter(status=2).first()
        date_start_work = first_recording_in_work.date_change_status
        return date_start_work.strftime('%d.%m.%Y %H:%M:%S')
    except:
        return f'Данные отсутствуют'


@register.simple_tag()
def get_who_change_status_done(id_task):
    try:
        tasks = ChangeStatusHistoryModel.objects.all().filter(print_task_id=id_task)
        last_recording_done = tasks.filter(status=3).last()
        emp_last = last_recording_done.emp
        print(f'get_who_change_status_done {emp_last}')
        return emp_last
    except:
        return f'Данные отсутствуют'


@register.simple_tag()
def get_when_change_status_done(id_task):
    try:
        tasks = ChangeStatusHistoryModel.objects.all().filter(print_task_id=id_task)
        last_recording_done = tasks.filter(status=3).last()
        date_last = last_recording_done.date_change_status
        print(f'get_when_change_status_done {date_last}')
        return date_last.strftime('%d.%m.%Y %H:%M:%S')
    except Exception as e:
        print(f'Exception: {e}')
        return f'Данные отсутствуют'
