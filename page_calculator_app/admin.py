from django.contrib import admin
from page_calculator_app.models import EmployeeModel, MoreDetailsEmployeeModel, PrintFilesModel, ListsFileModel, \
    PrintPagePermissionModel, ChangeStatusHistoryModel, CpeModel, OrdersModel, ObjectModel, ContractModel


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

class OrdersAdmin(admin.ModelAdmin):
    ordering = ["order"]
    search_fields = ["order", "order_name"]

class ObjectsAdmin(admin.ModelAdmin):
    ordering = ["object_code", "object_name"]
    search_fields = ["object_code", "object_name"]


class PrintFilesAdmin(admin.ModelAdmin):
    ordering = ['id']


class ChangeStatusHistoryAdmin(admin.ModelAdmin):
    ordering = ['-id']

class ContractAdmin(admin.ModelAdmin):
    ordering = ['contract_code']
    list_filter = ['contract_object']


admin.site.register(PrintFilesModel, PrintFilesAdmin)
admin.site.register(EmployeeModel, EmployeeAdmin)
admin.site.register(ChangeStatusHistoryModel, ChangeStatusHistoryAdmin)
admin.site.register(ListsFileModel)
admin.site.register(CpeModel)
admin.site.register(ObjectModel, ObjectsAdmin)
admin.site.register(ContractModel, ContractAdmin)
admin.site.register(OrdersModel, OrdersAdmin)
admin.site.register(PrintPagePermissionModel)
