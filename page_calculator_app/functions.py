import datetime
import time

from PIL import ImageStat

from .models import PrintFilesModel, EmployeeModel, ListsFileModel, OrdersModel, ObjectModel, ContractModel, \
    CountTasksModel, ChangeStatusHistoryModel
from pdf2image import convert_from_path


def check_date_in_db():
    today_year = f'{datetime.datetime.today().year}{str(datetime.datetime.today().month).rjust(2, "0")}{str(datetime.datetime.today().day).rjust(2, "0")}'
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


def save_status_log(print_task_id, print_task_status, emp_id):
    """Сохарнение лога"""
    new_history_log = ChangeStatusHistoryModel(
        print_task_id=print_task_id,
        status=print_task_status,
        emp_id=emp_id)
    new_history_log.save()


def check_color_pages(file_path, all_lists_file, lists_file_id):
    start_time = time.time()
    lists_file = ListsFileModel.objects.get(id=lists_file_id)
    pages = convert_from_path(file_path, 50, fmt='jpeg', poppler_path=r'C:\Program Files\poppler-24.02.0\Library\bin')
    print("Разбиралось на jpeg: --- %s seconds ---" % (time.time() - start_time))
    print(f'lists_file {lists_file}')
    for count, page in enumerate(pages):
        result_check_color = detect_color_image(page)
        # result_check_color = detect_color_image_v2(page)
        print(f'{count} - result_check_color: {result_check_color}')
        print(all_lists_file[count])
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
                lists_file.a2x3_color += 1
            elif all_lists_file[count][2] == 'A3x4':
                lists_file.a3x4 -= 1
                lists_file.a2x4_color += 1
            elif all_lists_file[count][2] == 'A3x5':
                lists_file.a3x5 -= 1
                lists_file.a2x5_color += 1
            elif all_lists_file[count][2] == 'A3x6':
                lists_file.a3x6 -= 1
                lists_file.a2x6_color += 1
            elif all_lists_file[count][2] == 'A3x7':
                lists_file.a3x7 -= 1
                lists_file.a2x7_color += 1
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
    print("--- %s seconds ---" % (time.time() - start_time))
    pass


def detect_color_image(file, thumb_size=40, MSE_cutoff=1, adjust_color_bias=True):
    # with Image.open(file, 'r') as img:
    #     print(img)
    pil_img = file
    bands = pil_img.getbands()
    if bands == ('R', 'G', 'B') or bands == ('R', 'G', 'B', 'A'):
        thumb = pil_img.resize((thumb_size, thumb_size))
        # thumb = pil_img
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
            # print("( MSE=", MSE, ")")
            return "grayscale"
        else:
            print("Color\t\t\t", )
            # print("( MSE=", MSE, ")")
            return True
    elif len(bands) == 1:
        print("Black and white", bands)
        return 'bw'
    else:
        print("Don't know...", bands)
        return 'dontknow'
