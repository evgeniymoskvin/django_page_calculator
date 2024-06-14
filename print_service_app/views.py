import ast

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.encoding import escape_uri_path

import mimetypes
import os.path

from random import randint
from page_calculator_app.models import PrintFilesModel, ListsFileModel


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
        try:
            obj_info = ListsFileModel.objects.get(print_file_id=obj.id)
            bad_lists = obj_info.other_pages
            dict_temp_file_json = ast.literal_eval(bad_lists)
        except:
            obj_info = None

        content = {'obj': obj,
                   'obj_info': obj_info,
                   'bad_lists': dict_temp_file_json}
        return render(request, 'print_service_app/ajax/modal_details_task.html', content)

    def post(self, request):
        print(request.POST)
        # obj_id_for_change_status': ['32'], 'TypeWorkTask_id': ['2']

        return HttpResponse(status=200)

class DownloadFileView(View):
    def get(self, request, pk):
        file_path_in_db = PrintFilesModel.objects.get(id=pk)
        # print(file_path_in_db.file)
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_path_in_db.file_to_print))
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(file_path)
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'inline; filename=' + escape_uri_path(os.path.basename(file_path))
                return response
        raise Http404
