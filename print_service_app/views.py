from django.shortcuts import render
from django.views import View
from random import randint
from page_calculator_app.models import PrintFilesModel


# Create your views here.
class IndexView(View):
    def get(self, request):
        content = {"tasks_to_print": "Идет загрузка"}
        return render(request, 'print_service_app/index.html', content)


def get_tasks(request):
    print('сработал функция get_tasks')
    # value = randint(1, 100)
    # content = {'value': value}

    tasks_to_print = PrintFilesModel.objects.get_queryset().filter(status=1).order_by('-id')
    content = {"tasks_to_print": tasks_to_print}

    return render(request, 'print_service_app/ajax/get_task_list.html', content)

class GetInfoPrintTaskView(View):
    def get(self, request):
        obj_id = int(request.GET.get('object'))
        obj = PrintFilesModel.objects.get(id=obj_id)
        content = {'obj': obj}
        return render(request, 'print_service_app/ajax/modal_details_task.html', content)
