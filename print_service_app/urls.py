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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('new-tasks-to-print', views.IndexView.as_view(), name='new-tasks'),
    path('all-tasks', views.AllTaskView.as_view(), name='all-tasks'),
    path('ajax/get-list', views.get_tasks, name='get-tasks-print'),
    path('ajax/get-info', views.GetInfoPrintTaskView.as_view(), name='get-info-task-print'),
    path('ajax/get-report-info', views.GetInfoReportPrintTaskView.as_view(), name='get-info-report-task-print'),
    path('download_file/<int:pk>', views.DownloadFileView.as_view(), name='download_file'),
    path('download_blank/<int:pk>', views.DownloadBlankView.as_view(), name='download_blank'),
    path('blank/<int:pk>', views.BlankPageView.as_view(), name='blank'),
    path('report/', views.ReportView.as_view(), name='report'),

]
