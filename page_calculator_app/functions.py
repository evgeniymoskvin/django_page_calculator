import datetime
from .models import PrintFilesModel, EmployeeModel, OrdersModel, ObjectModel, ContractModel, CountTasksModel


def check_date_in_db():
    today_year = f'{datetime.datetime.today().year}{str(datetime.datetime.today().month).rjust(2, "0")}{datetime.datetime.today().day}'
    try:
        last_task_in_db = CountTasksModel.objects.latest('id')
        print(f'try:{last_task_in_db}')
    except Exception as e:
        last_task_in_db = CountTasksModel(date_of_print=today_year)
        last_task_in_db.save()
        print(e)
    if last_task_in_db.date_of_print != today_year:
        new_count = CountTasksModel(date_of_print=today_year)
        print(f'new_count:{new_count}')
        new_count.save()