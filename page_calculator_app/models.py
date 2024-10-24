from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator

from os import path


class OrdersModel(models.Model):
    """    Таблица номеров заказов    """
    order = models.CharField("Номер заказчика", null=True, max_length=10, blank=True)
    order_name = models.CharField(verbose_name="Наименование заказчика", null=True, blank=True, max_length=250)

    class Meta:
        verbose_name = _("номер заказчика")
        verbose_name_plural = _("номера заказчиков")
        managed = False
        db_table = 'ToDo_tasks_ordersmodel'

    def __str__(self):
        return f'{self.order} - {self.order_name}'


class ObjectModel(models.Model):
    """Таблица с наименованиями объектов"""
    object_name = models.CharField("Наименование объекта", max_length=250, default=None)
    object_code = models.CharField(verbose_name="Код объекта", max_length=10, null=True, blank=True)
    show = models.BooleanField("Отображать объект", default=True)

    class Meta:
        verbose_name = _("наименование объекта")
        verbose_name_plural = _("наименования объектов")
        managed = False
        db_table = 'ToDo_tasks_objectmodel'

    def __str__(self):
        return f'{self.object_code} - {self.object_name}'


class ContractModel(models.Model):
    """Таблица договоров"""
    contract_object = models.ForeignKey(ObjectModel, on_delete=models.PROTECT, verbose_name="Объект", default=1)
    contract_name = models.CharField(max_length=650, verbose_name="Номер договора")
    contract_code = models.CharField(max_length=500, verbose_name="Код договора", null=True, blank=True)
    show = models.BooleanField("Отображать договор", default=True)
    show_in_print = models.BooleanField("Отображать только в печати", default=False)

    class Meta:
        verbose_name = _("номер договора")
        verbose_name_plural = _("номера договоров")
        managed = False
        db_table = 'ToDo_tasks_contractmodel'

    def __str__(self):
        return f'{self.contract_object}, {self.contract_name}'


class JobTitleModel(models.Model):
    """ Таблица должностей """

    job_title = models.CharField("Должность", max_length=200)

    class Meta:
        verbose_name = _("должность")
        verbose_name_plural = _("должности")
        managed = False
        db_table = 'ToDo_tasks_jobtitlemodel'

    def __str__(self):
        return f'{self.job_title}'


class CityDepModel(models.Model):
    """Таблица городов"""
    city = models.CharField(verbose_name="Город", max_length=100)
    name_dep = models.CharField(verbose_name="Наименование организации", max_length=350)

    class Meta:
        managed = False
        verbose_name = _("город/организация")
        verbose_name_plural = _("города/организации")
        db_table = 'admin_panel_app_citydepmodel'

    def __str__(self):
        return f'{self.city} - {self.name_dep}'


class GroupDepartmentModel(models.Model):
    """Таблица управлений"""
    group_dep_abr = models.CharField("Сокращенное название управления", max_length=10)
    group_dep_name = models.CharField("Полное название управления", max_length=250)
    city_dep = models.ForeignKey(CityDepModel, verbose_name="Город", on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField("Отображать отдел", default=True)

    def __str__(self):
        return f'{self.group_dep_abr}, {self.group_dep_name}'

    class Meta:
        verbose_name = _("управление")
        verbose_name_plural = _("управления")
        managed = False
        db_table = 'ToDo_tasks_groupdepartmentmodel'


class CommandNumberModel(models.Model):
    """Таблица отделов"""
    command_number = models.IntegerField("Номер отдела/Сокращение")
    command_name = models.CharField("Наименование отдела", max_length=150)
    department = models.ForeignKey(GroupDepartmentModel, verbose_name="Управление", on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True)
    show = models.BooleanField("Отображать отдел", default=True)

    def __str__(self):
        return f'{self.command_number}, {self.command_name}'

    class Meta:
        verbose_name = _("номер отдела")
        verbose_name_plural = _("номера отделов")
        managed = False
        db_table = 'ToDo_tasks_commandnumbermodel'


class EmployeeModel(models.Model):
    """Таблица сотрудников"""
    user = models.OneToOneField(User, models.PROTECT, verbose_name="Пользователь", related_name='phonebook_emp_user')
    last_name = models.CharField("Фамилия", max_length=150)
    first_name = models.CharField("Имя", max_length=150)
    middle_name = models.CharField("Отчество", max_length=150)
    personnel_number = models.CharField("Табельный номер", max_length=20, null=True, default=None)
    job_title = models.ForeignKey(JobTitleModel, on_delete=models.PROTECT, null=True, verbose_name="Должность")
    department = models.ForeignKey(CommandNumberModel, on_delete=models.PROTECT, null=True, verbose_name="№ отдела")
    user_phone = models.IntegerField("№ телефона внутренний", null=True, default=None, blank=True)
    department_group = models.ForeignKey(GroupDepartmentModel, on_delete=models.SET_NULL, default=None, null=True,
                                         verbose_name="Управление")
    right_to_sign = models.BooleanField(verbose_name="Право подписывать задания", default=False)
    check_edit = models.BooleanField("Возможность редактирования задания", default=True)
    can_make_task = models.BooleanField("Возможность выдавать задания", default=True)
    cpe_flag = models.BooleanField("Флаг ГИП (техническая метка)", default=False)
    mailing_list_check = models.BooleanField("Получать рассылку", default=True)
    work_status = models.BooleanField("Сотрудник работает", default=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'

    class Meta:
        managed = False
        verbose_name = _("сотрудник")
        verbose_name_plural = _("сотрудники")
        db_table = 'ToDo_tasks_employee'


def upload_to(instance, filename):
    name_to_path = str(instance.emp.id)
    new_path = path.join('files',
                         # "media", filename)
                         name_to_path,
                         filename)
    print(new_path)
    return new_path


class MoreDetailsEmployeeModel(models.Model):
    """Дополнительная информация по сотрудникам"""
    emp = models.OneToOneField(EmployeeModel, models.CASCADE, verbose_name="Пользователь")
    photo = models.ImageField(verbose_name="Файл", null=True, blank=True,
                              upload_to=upload_to)
    outside_email = models.EmailField(verbose_name="Внешняя почта", null=True, blank=True)
    mobile_phone = models.CharField(verbose_name="Мобильный телефон", null=True, blank=True, max_length=30)
    date_birthday = models.DateField(verbose_name="День рождения", null=True, blank=True)
    room = models.CharField(verbose_name="Номер комнаты", null=True, blank=True, max_length=30)
    date_birthday_show = models.BooleanField(verbose_name="Отображать день рождения", default=False, null=True)
    city_dep = models.ForeignKey(CityDepModel, on_delete=models.PROTECT, null=True, verbose_name="Город/Подразделение",
                                 blank=True)
    send_email_salary_blank = models.BooleanField(verbose_name="Отсылать расчетный листок", default=False)

    class Meta:
        managed = False
        verbose_name = _("дополнительная информация по сотруднику")
        verbose_name_plural = _("дополнительная информация по сотрудникам")
        db_table = 'admin_panel_app_moredetailsemployeemodel'

    def __str__(self):
        return f'{self.emp}'


class CpeModel(models.Model):
    """Таблица ГИП-ов"""
    cpe_user = models.ForeignKey(EmployeeModel, on_delete=models.SET_NULL, verbose_name="Сотрудник", null=True)
    cpe_object = models.ForeignKey(ObjectModel, on_delete=models.PROTECT, verbose_name="Объект", null=True)
    cpe_important = models.BooleanField(verbose_name='Главный за объект', default=False)

    class Meta:
        verbose_name = _("ГИП")
        verbose_name_plural = _("ГИПЫ")
        managed = False
        db_table = 'ToDo_tasks_cpemodel'

    def __str__(self):
        return f'{self.cpe_user}, {self.cpe_object}'


def upload_print_file(instance, filename):
    """Функция присваивания пути хранения загружаемому файлу"""
    # name_to_path = str(instance.emp.id)
    new_path = path.join('files', 'print_files', f'{datetime.now().year}{datetime.now().month}{datetime.now().day}',
                         # "media", filename)
                         # name_to_path,
                         filename)
    print(new_path)
    return new_path


class MarkDocModel(models.Model):
    """Таблица марок документации"""
    mark_doc = models.CharField("Краткое название марки", max_length=5)
    mark_doc_full_name = models.CharField("Полное название", max_length=150)

    class Meta:
        verbose_name = _("марка документации")
        verbose_name_plural = _("марки документации")
        managed = False
        db_table = 'ToDo_tasks_markdocmodel'

    def __str__(self):
        return f'{self.mark_doc} - {self.mark_doc_full_name}'


class ArchivePrintModel(models.Model):
    class TypeTask(models.IntegerChoices):
        """Тип печати"""
        TITLES = 2, _('Для аннулирования (печать титульного листа и обложки)')
        CHANGES = 1, _('Для внесения изменений (печать альбома целиком)')

    """Таблица печать файла из архива"""
    permission_number = models.CharField(verbose_name="Номер разрешения", max_length=15, null=True, blank=True)
    purpose_of_printing = models.IntegerField("Тип вносимых изменений:", choices=TypeTask.choices, default=0)

    class Meta:
        verbose_name = _('информация печати из архива')
        verbose_name_plural = _("информация печати из архива")

    def __str__(self):
        return f'{self.permission_number} - {self.purpose_of_printing}'


class PrintFilesModel(models.Model):
    """Таблица задач на печать"""

    class TypeTask(models.IntegerChoices):
        """        Выбор вида документации        """
        NONETASK = 0, _('Не указан')
        Scan = 1, _('Скан')
        Print = 2, _('Печать')
        Copy = 3, _('Тираж')

    class TypeWorkTask(models.IntegerChoices):
        """        Выбор вида документации        """
        WD = 0, _('Не указан')
        RD = 1, _('РД')
        PD = 2, _('ПД')
        OBIN = 3, _('ОБИН')
        NIOKR = 4, _('НИОКР')

    class PrintFileStatusChoice(models.IntegerChoices):
        """Статус кода Kks"""
        CANCELED = 0, _('Отменен')
        ACTUAL = 1, _('Актуален')
        WORK = 2, _('В работе')
        DONE = 3, _('Готов')

    filename = models.CharField(verbose_name="Название файла", max_length=150, null=True, blank=True)
    inventory_number_file = models.CharField(verbose_name="Инвентарный номер", max_length=150)
    emp_upload_file = models.ForeignKey(EmployeeModel, null=False, blank=True, on_delete=models.CASCADE,
                                        verbose_name="Пользователь загрузивший файл")
    status = models.IntegerField(verbose_name="Статус номера", choices=PrintFileStatusChoice.choices, default=1)
    file_to_print = models.FileField(storage=FileSystemStorage(), verbose_name="Файл на печать", null=True, blank=True,
                                     upload_to=upload_print_file)
    add_file_date = models.DateTimeField('Дата создания', auto_now_add=True, null=True)
    date_change_status = models.DateTimeField('Дата распечатки', null=True, blank=True)
    task_type_work = models.IntegerField("Вид документации:", choices=TypeWorkTask.choices, default=0)
    order = models.ForeignKey(OrdersModel, verbose_name='Номер заказа', null=True, blank=True,
                              on_delete=models.SET_NULL)
    object = models.ForeignKey(ObjectModel, verbose_name='Объект', null=True, blank=True, on_delete=models.SET_NULL)
    contract = models.ForeignKey(ContractModel, verbose_name='Договор', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    copy_count = models.IntegerField(verbose_name='Количество копий', default=1, blank=True)
    inventory_number_request = models.CharField(verbose_name="Номер заявки", max_length=100, blank=True, null=True)
    type_task = models.IntegerField(verbose_name="Тип задачи", choices=TypeTask.choices, default=0)
    count_pages = models.IntegerField(verbose_name="Количество листов", null=True, blank=True, default=0)
    a4_count_formats = models.IntegerField(verbose_name="Количество форматов а4", null=True, blank=True, default=0)
    user_clearance = models.IntegerField(verbose_name='Допуск подсчета у пользователя', null=True, blank=True,
                                         default=0)
    print_folding = models.BooleanField(verbose_name='Фальцовка', null=True, blank=True, default=False)
    color = models.BooleanField(verbose_name='Цветное', null=True, blank=True, default=False)
    mark_print_file = models.ForeignKey(MarkDocModel, verbose_name='Марка документации', null=True, blank=True,
                                        on_delete=models.SET_NULL, default=None)
    print_from_archive = models.BooleanField(verbose_name='Печать из архива', default=False)
    print_from_archive_details = models.OneToOneField(ArchivePrintModel, verbose_name="Детали печати из архива",
                                                   default=None, null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.CharField(verbose_name='Комментарий', null=True, blank=True, max_length=500)

    class Meta:
        verbose_name = _('файл на печать')
        verbose_name_plural = _("файлы на печать")

    def __str__(self):
        return f'{self.inventory_number_request}: {self.filename} | {self.status} | {self.add_file_date} ({self.date_change_status})'


class ListsFileModel(models.Model):
    """
    Таблица с количеством листов по задачам
    """
    print_file = models.OneToOneField(PrintFilesModel, on_delete=models.CASCADE, null=False, blank=False)
    a0 = models.IntegerField(verbose_name="A0", default=0, blank=True)
    a0_color = models.IntegerField(verbose_name="A0_color", default=0, blank=True)
    a0x2 = models.IntegerField(verbose_name="A0x2", default=0, blank=True)
    a0x2_color = models.IntegerField(verbose_name="A0x2_color", default=0, blank=True)
    a0x3 = models.IntegerField(verbose_name="A0x3", default=0, blank=True)
    a0x3_color = models.IntegerField(verbose_name="A0x3_color", default=0, blank=True)
    a1 = models.IntegerField(verbose_name="A1", default=0, blank=True)
    a1_color = models.IntegerField(verbose_name="A1_color", default=0, blank=True)
    a1x3 = models.IntegerField(verbose_name="A1x3", default=0, blank=True)
    a1x3_color = models.IntegerField(verbose_name="A1x3_color", default=0, blank=True)
    a1x4 = models.IntegerField(verbose_name="A1x4", default=0, blank=True)
    a1x4_color = models.IntegerField(verbose_name="A1x4_color", default=0, blank=True)
    a2 = models.IntegerField(verbose_name="A2", default=0, blank=True)
    a2_color = models.IntegerField(verbose_name="A2_color", default=0, blank=True)
    a2x3 = models.IntegerField(verbose_name="A2x3", default=0, blank=True)
    a2x3_color = models.IntegerField(verbose_name="A2x3_color", default=0, blank=True)
    a2x4 = models.IntegerField(verbose_name="A2x4", default=0, blank=True)
    a2x4_color = models.IntegerField(verbose_name="A2x4_color", default=0, blank=True)
    a2x5 = models.IntegerField(verbose_name="A2x5", default=0, blank=True)
    a2x5_color = models.IntegerField(verbose_name="A2x5_color", default=0, blank=True)
    a3 = models.IntegerField(verbose_name="A3", default=0, blank=True)
    a3_color = models.IntegerField(verbose_name="A3_color", default=0, blank=True)
    a3x3 = models.IntegerField(verbose_name="A3x3", default=0, blank=True)
    a3x3_color = models.IntegerField(verbose_name="A3x3_color", default=0, blank=True)
    a3x4 = models.IntegerField(verbose_name="A3x4", default=0, blank=True)
    a3x4_color = models.IntegerField(verbose_name="A3x4_color", default=0, blank=True)
    a3x5 = models.IntegerField(verbose_name="A3x5", default=0, blank=True)
    a3x5_color = models.IntegerField(verbose_name="A3x5_color", default=0, blank=True)
    a3x6 = models.IntegerField(verbose_name="A3x6", default=0, blank=True)
    a3x6_color = models.IntegerField(verbose_name="A3x6_color", default=0, blank=True)
    a3x7 = models.IntegerField(verbose_name="A3x7", default=0, blank=True)
    a3x7_color = models.IntegerField(verbose_name="A3x7_color", default=0, blank=True)
    a4 = models.IntegerField(verbose_name="A4", default=0, blank=True)
    a4_color = models.IntegerField(verbose_name="A4_color", default=0, blank=True)
    a4x3 = models.IntegerField(verbose_name="A4x3", default=0, blank=True)
    a4x3_color = models.IntegerField(verbose_name="A4x3_color", default=0, blank=True)
    a4x4 = models.IntegerField(verbose_name="A4x4", default=0, blank=True)
    a4x4_color = models.IntegerField(verbose_name="A4x4_color", default=0, blank=True)
    a4x5 = models.IntegerField(verbose_name="A4x5", default=0, blank=True)
    a4x5_color = models.IntegerField(verbose_name="A4x5_color", default=0, blank=True)
    a4x6 = models.IntegerField(verbose_name="A4x6", default=0, blank=True)
    a4x6_color = models.IntegerField(verbose_name="A4x6_color", default=0, blank=True)
    a4x7 = models.IntegerField(verbose_name="A4x7", default=0, blank=True)
    a4x7_color = models.IntegerField(verbose_name="A4x7_color", default=0, blank=True)
    a4x8 = models.IntegerField(verbose_name="A4x8", default=0, blank=True)
    a4x8_color = models.IntegerField(verbose_name="A4x8_color", default=0, blank=True)
    a4x9 = models.IntegerField(verbose_name="A4x9", default=0, blank=True)
    a4x9_color = models.IntegerField(verbose_name="A4x9_color", default=0, blank=True)
    other_pages = models.CharField(verbose_name="Другое", max_length=1000, blank=True, null=True)
    other_pages_color = models.CharField(verbose_name="Другое_color", max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = _('лист файла')
        verbose_name_plural = _("листы файлов")

    def __str__(self):
        return f'{self.print_file.inventory_number_request} | {self.print_file.inventory_number_file}'


class PrintPagePermissionModel(models.Model):
    """
    Доступ сотрудников к странице печати
    """
    emp = models.ForeignKey(EmployeeModel, verbose_name="Сотрудник", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('сотрудник имеющий доступ к странице печати')
        verbose_name_plural = _('сотрудники имеющие доступ к странице печати')

    def __str__(self):
        return f'{self.emp.last_name} {self.emp.first_name} {self.emp.middle_name}'


class CountTasksModel(models.Model):
    """
    Счетчик задач за каждый день
    """
    count = models.IntegerField(verbose_name='Количество заявок', default=0)
    date_of_print = models.CharField(verbose_name='Дата обработки заявок', max_length=150)
    auto_date = models.DateTimeField('Дата для сортировок', auto_now_add=True, null=True)

    class Meta:
        verbose_name = _('счетчик печати')
        verbose_name_plural = _('счетчики печати')

    def __str__(self):
        return f'{self.date_of_print} - {self.count}'


class ChangeStatusHistoryModel(models.Model):
    """
    Лог изменения статусов задач
    """

    class PrintFileStatusChoice(models.IntegerChoices):
        """Статус кода Kks"""
        CANCELED = 0, _('Аннулирован')
        ACTUAL = 1, _('Актуален')
        WORK = 2, _('В работе')
        DONE = 3, _('Готов')

    """История изменения статусов"""
    print_task = models.ForeignKey(PrintFilesModel, verbose_name='Задание на печать', on_delete=models.CASCADE,
                                   default=None, null=True, blank=True)
    status = models.IntegerField(verbose_name="Статус номера", choices=PrintFileStatusChoice.choices, default=1)
    emp = models.ForeignKey(EmployeeModel, verbose_name='Сотрудник', on_delete=models.CASCADE, default=None, null=True,
                            blank=True)
    date_change_status = models.DateTimeField('Дата изменения', auto_now_add=True, null=True)

    class Meta:
        verbose_name = _('история изменения')
        verbose_name_plural = _('история изменений')

    def __str__(self):
        return f'{self.print_task.inventory_number_request} | {self.status} | {self.emp} | {self.date_change_status}'
