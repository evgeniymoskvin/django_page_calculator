"""
URL configuration for django_page_calculator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.StartPageView.as_view(), name='start'),
    path('index', views.IndexView.as_view(), name='index'),
    path('my-print-tasks', views.MyPrintTaskView.as_view(), name='my-print-tasks'),
    path('delete-files/<int:pk>', views.DeleteFileView.as_view(), name='delete-file'),
    path('ajax/answer', views.GetAnswerView.as_view(), name='get-answer'),
    path('ajax/change-clearance', views.ChangeClearanceView.as_view(), name='change-clearance'),
    # path('ajax/get-blanc', views.GetBlancView.as_view(), name='get-blanc'),
    path('ajax/print-send', views.PrintView.as_view(), name='print-send'),
    path('ajax/get-my-task-info', views.GetInfoMyTaskView.as_view(), name='get-my-task-info'),
    path('ajax/cancel-task-print', views.CancelMyTaskView.as_view(), name='cancel-task-print'),
    path('ajax/get-contracts', views.get_contracts, name='get-contracts'),
]
