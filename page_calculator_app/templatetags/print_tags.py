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

# @register.simple_tag()
# def get_who_change_status(id_task):
#     tasks = ChangeStatusHistoryModel.objects.get_queryset(print_task_id=id_task)
#     first_recording_in_work = tasks.filter(status=2).first()
#     last_
