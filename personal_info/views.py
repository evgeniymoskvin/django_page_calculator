from django.shortcuts import render
from django.views import View

from page_calculator_app.models import PrintFilesModel, ListsFileModel, EmployeeModel, PrintPagePermissionModel, \
    ChangeStatusHistoryModel, OrdersModel, ObjectModel, ContractModel, MarkDocModel, ArchivePrintModel, MoreDetailsEmployeeModel

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from .forms import UserPasswordChangeForm


class PersonalInfoView(View):
    """Информация о пользователе"""

    def get(self, request):
        emp = EmployeeModel.objects.get(user=request.user)
        emp_more_info = MoreDetailsEmployeeModel.objects.get(emp=emp)
        content = {
            'emp': emp,
            'emp_more_info': emp_more_info
        }
        return render(request, 'personal_info/personal_info.html', content)


class ChangeUserPasswordView(SuccessMessageMixin, PasswordChangeView):
    """
    Изменение пароля пользователя
    """
    form_class = UserPasswordChangeForm
    template_name = 'personal_info/change_password.html'
    success_message = 'Ваш пароль был успешно изменён!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменение пароля на сайте'
        return context

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'slug': self.request.user.profile.slug})
