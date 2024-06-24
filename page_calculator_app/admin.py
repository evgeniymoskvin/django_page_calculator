from django.contrib import admin
from page_calculator_app.models import EmployeeModel, MoreDetailsEmployeeModel, PrintFilesModel, ListsFileModel, PrintPagePermissionModel

class EmployeeAdmin(admin.ModelAdmin):
    # list_display = ("author", "text_task")
    ordering = ["-work_status", "last_name", "first_name", "middle_name"]
    search_fields = ["last_name", "first_name", "middle_name", "personnel_number", "user_phone"]
    list_filter = ("department_group__city_dep__city", "department_group__group_dep_abr", "department__command_number")


class MoreDetailsEmployeeAdmin(admin.ModelAdmin):
    ordering = ["emp__last_name", "emp__first_name", "emp__middle_name", ]
    search_fields = ["emp__last_name", "emp__first_name", "emp__middle_name"]
    list_filter = (
        "emp__department_group__city_dep__city", "emp__department_group__group_dep_abr",
        "emp__department__command_number")

class PrintFilesAdmin(admin.ModelAdmin):
    ordering = ['id']


admin.site.register(PrintFilesModel, PrintFilesAdmin)
admin.site.register(EmployeeModel, EmployeeAdmin)
admin.site.register(ListsFileModel)
admin.site.register(PrintPagePermissionModel)