from django.shortcuts import render, redirect
from django.views import View
from .forms import UploadFileForm
import time
from django.http import HttpResponse
import mimetypes
from django.http import HttpResponse

import json
import ast

import math
import PyPDF2

PAGE_SIZE_STANDARD = {
    'A0': (841, 1189, 16),
    'A0x2': (1189, 1682, 32),
    'A0x3': (1189, 2523, 48),
    'A1': (594, 841, 8),
    'A1x3': (841, 1783, 24),
    'A1x4': (841, 2378, 32),
    'A2': (420, 594, 4),
    'A2x3': (594, 1261, 12),
    'A2x4': (594, 1682, 16),
    'A2x5': (594, 2102, 20),
    'A3': (297, 420, 2),
    'A3x3': (420, 891, 6),
    'A3x4': (420, 1189, 8),
    'A3x5': (420, 1486, 10),
    'A3x6': (420, 1783, 12),
    'A3x7': (420, 2080, 14),
    'A4': (210, 297, 1),
    'A4x3': (297, 630, 3),
    'A4x4': (297, 841, 4),
    'A4x5': (297, 1051, 5),
    'A4x6': (297, 1261, 6),
    'A4x7': (297, 1471, 7),
    'A4x8': (297, 1682, 8),
    'A4x9': (297, 1892, 9),
}


def handle_uploaded_file(f):
    with open(f"{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


class IndexView(View):
    def get(self, request):
        try:
            clearance = int(request.COOKIES['clearance'])
        except:
            clearance = 15
        form = UploadFileForm()
        content = {'form': form,
                   'clearance': clearance}
        return render(request, 'page_calculator_app/index.html', content)


class GetAnswerView(View):
    def post(self, request):
        # time.sleep(1)
        try:
            clearance = int(request.COOKIES['clearance'])
        except:
            clearance = 15
        files_count = 0  # Счетчик файлов
        all_files_format = 0  # Счетчик форматов А4 по всем файлам
        all_lists_approve = 0  # Счетчик распознанных листов
        all_lists_count = 0  # Всего листов во всех файлах
        errors = 0  # Ошибок по файлам

        print(f'request.POST: {request.POST}')
        print(f'request.FILES: {request.FILES}')
        print(f'request.COOKIES: {request.COOKIES}')
        print('-----------------------')
        print(f'Подсчет с допуском {clearance}мм')
        print('-----------------------')
        # Итоговый словарь с перечнем файлов
        exit_dict = {}

        for file in request.FILES.getlist('file'):
            files_count += 1
            print(file, file.content_type)
            try:
                # Пустой словарь для подсчета листов
                pdf_size_file = {
                    'A0': 0,
                    'A0x2': 0,
                    'A0x3': 0,
                    'A1': 0,
                    'A1x3': 0,
                    'A1x4': 0,
                    'A2': 0,
                    'A2x3': 0,
                    'A2x4': 0,
                    'A2x5': 0,
                    'A3': 0,
                    'A3x3': 0,
                    'A3x4': 0,
                    'A3x5': 0,
                    'A3x6': 0,
                    'A3x7': 0,
                    'A4': 0,
                    'A4x3': 0,
                    'A4x4': 0,
                    'A4x5': 0,
                    'A4x6': 0,
                    'A4x7': 0,
                    'A4x8': 0,
                    'A4x9': 0,
                }
                pdf_unknown_size_file = {}
                a4_count = 0  # Счетчик форматов А4
                normal_pages = 0  # Счетчик распознанных листов
                list_pages = []  # Список листов

                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                all_lists_count += num_pages
                for i in range(num_pages):
                    checker = 0
                    box = pdf_reader.pages[i]
                    # Переводим значения в миллиметры
                    width = math.ceil(float(box.mediabox.width) * 0.35273159)
                    height = math.ceil(float(box.mediabox.height) * 0.35273159)
                    # list_pages.append([height, width])
                    # Приводим к одной ориентации
                    if width < height:
                        small = width
                        long = height
                    else:
                        small = height
                        long = width
                    # Проверяем вхождение данных размеров в стандартные, с допуском 15мм
                    for key, value in PAGE_SIZE_STANDARD.items():
                        if (value[0] >= small - clearance) and (value[0] <= small + clearance) and (
                                value[1] <= long + clearance) and (
                                value[1] >= long - clearance):
                            normal_pages += 1
                            a4_count += value[2]
                            pdf_size_file[key] += 1
                            checker = 1
                            list_pages.append([height, width, key])
                    # Если в стандартные значения не вошли
                    if checker == 0:
                        size = f'{small}x{long}'
                        list_pages.append([height, width, 0])
                        try:
                            pdf_unknown_size_file[size] += 1  # Если такой размер уже есть в словаре
                        except:
                            pdf_unknown_size_file[size] = 1

                temp_list = []
                # Создаем словарь с пустыми значениями.
                for key, value in pdf_size_file.items():
                    if value == 0:
                        temp_list.append(key)
                # Удаляем из словаря все пустые значения
                for i in temp_list:
                    del pdf_size_file[i]
                final_list = []
                for key, value in pdf_size_file.items():
                    if value > 0:
                        final_list.append([key, value])
                print(f'pdf_size_file {pdf_size_file}')
                good_lists = pdf_size_file.copy()

                num_pages = len(pdf_reader.pages)
                exit_dict[file.name] = pdf_size_file
                exit_dict[file.name]['good_lists'] = good_lists
                exit_dict[file.name]['count_pages'] = num_pages
                exit_dict[file.name]['pdf_unknown_size_file'] = pdf_unknown_size_file
                exit_dict[file.name]['len_pdf_unknown_size_file'] = len(pdf_unknown_size_file)
                exit_dict[file.name]['list_pages'] = list_pages
                exit_dict[file.name]['normal_pages'] = normal_pages
                exit_dict[file.name]['a4_count'] = a4_count
                all_lists_approve += normal_pages
                all_files_format += a4_count
            except:
                exit_dict[file.name] = {}
                exit_dict[file.name]['error'] = 1
                errors += 1
            print('-----------------------')
        content = {'all_lists_count': all_lists_count,
                   'files_count': files_count,
                   'all_lists_approve': all_lists_approve,
                   'all_files_format': all_files_format,
                   # 'pdf_size_file': pdf_size_file,
                   'exit_dict': exit_dict,
                   'clearance': clearance,
                   'errors': errors,
                   'good_files': files_count - errors,
                   }
        # content = {
        #            'pdf_size_file': pdf_size_file}
        resp = render(request, 'page_calculator_app/answer.html', content)
        resp.set_cookie(key='clearance', value=clearance)
        return resp


class ChangeClearanceView(View):
    def post(self, request):
        clearance = int(request.POST.get('input_clearance_value'))
        print(clearance)
        print(f'request.POST: {request.POST}')
        print(f'request.FILES: {request.FILES}')
        print(f'request.COOKIES: {request.COOKIES}')
        resp = HttpResponse(status=200)
        resp.set_cookie('clearance', clearance)
        return resp

class GetBlancView(View):
    def get (self, request):
        print(f'request.GET: {request.GET}')
        print(f'request.FILES: {request.FILES}')
        print(f'request.COOKIES: {request.COOKIES}')
        json_result = request.GET['json']
        print(json_result)
        print(type(json_result))
        dict_result = ast.literal_eval(json_result)
        print(dict_result)
        print(type(dict_result))

        return HttpResponse(status=200)

class PrintView(View):
    def get (self, request):
        print(f'request.GET: {request.GET}')
        print(f'request.FILES: {request.FILES}')
        print(f'request.COOKIES: {request.COOKIES}')

        return HttpResponse(status=200)