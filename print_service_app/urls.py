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
    path('ajax/get-notification', views.get_tasks_count, name='get-notification'),
    path('ajax/get-all-task', views.get_all_task, name='get-all-task'),
    path('ajax/get-info', views.GetInfoPrintTaskView.as_view(), name='get-info-task-print'),
    path('ajax/get-edit-modal', views.GetEditModalWindow.as_view(), name='get-edit-modal'),
    path('ajax/get-add-file-modal', views.AddArchiveFileView.as_view(), name='get-add-file-modal'),
    path('ajax/get-edit-lists-modal', views.GetEditListsModalWindow.as_view(), name='get-edit-lists-modal'),
    path('ajax/get-report-info', views.GetInfoReportPrintTaskView.as_view(), name='get-info-report-task-print'),
    path('download_file/<int:pk>', views.DownloadFileView.as_view(), name='download_file'),
    path('download_blank/<int:pk>', views.DownloadBlankView.as_view(), name='download_blank'),
    path('blank/<int:pk>', views.BlankPageView.as_view(), name='blank'),
    path('report_xls/<int:pk>', views.GeneratePrintReportTableView.as_view(), name='generate_report_table'),
    path('report_dispatcher_xls/<int:pk>', views.GenerateDispatcherReportTableView.as_view(),
         name='generate_dispatcher_report'),
    path('report/', views.ReportView.as_view(), name='report'),
    path('download_report/', views.DownloadExportReportView.as_view(), name='download-report'),
    path('download_dispatcher_report/', views.DownloadDispatcherExportReportView.as_view(), name='download-dispatcher-report'),
    path('report-list/', views.GeneratePrintReportListTableView.as_view(), name='generate_report_table_list'),
    path('report-disapetcher-list/', views.GenerateDispatcherReportListTableView.as_view(), name='generate_dispatchet_report_table_list'),
    path('service/clear-files', views.DeleteOldFiles.as_view(), name='clear-files'),

]
