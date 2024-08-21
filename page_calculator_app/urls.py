from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.StartPageView.as_view(), name='start'),
    path('index', views.IndexView.as_view(), name='index'),
    path('my-print-tasks', views.MyPrintTaskView.as_view(), name='my-print-tasks'),
    path('delete-files/<int:pk>', views.DeleteFileView.as_view(), name='delete-file'),
    path('ajax/answer', views.GetAnswerView.as_view(), name='get-answer'),
    path('ajax/change-clearance', views.ChangeClearanceView.as_view(), name='change-clearance'),
    path('ajax/print-send', views.PrintView.as_view(), name='print-send'),
    path('ajax/get-my-task-info', views.GetInfoMyTaskView.as_view(), name='get-my-task-info'),
    path('ajax/cancel-task-print', views.CancelMyTaskView.as_view(), name='cancel-task-print'),
    path('ajax/get-contracts', views.get_contracts, name='get-contracts'),
]
