from django.urls import path
from . import views

app_name = 'housekeeping'

urlpatterns = [
    path('', views.housekeeping_dashboard, name='dashboard'),

    path('cleaning/', views.cleaning_list, name='cleaning_list'),
    path('cleaning/create/', views.create_cleaning_task, name='create_cleaning_task'),
    path('cleaning/<int:task_id>/start/', views.start_cleaning, name='start_cleaning'),
    path('cleaning/<int:task_id>/complete/', views.complete_cleaning, name='complete_cleaning'),
    path('cleaning/<int:task_id>/inspect/', views.inspect_cleaning, name='inspect_cleaning'),

    path('laundry/', views.laundry_list, name='laundry_list'),
    path('laundry/create/', views.create_laundry_request, name='create_laundry_request'),
    path('laundry/<int:request_id>/deliver/', views.deliver_laundry, name='deliver_laundry'),

    path('lost-found/', views.lost_found_list, name='lost_found_list'),
    path('lost-found/create/', views.create_lost_found, name='create_lost_found'),

    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/create/', views.create_maintenance_issue, name='create_maintenance_issue'),

    path('reports/', views.housekeeping_report, name='housekeeping_report'),
    path('reports/pdf/', views.download_housekeeping_report_pdf, name='download_housekeeping_report_pdf'),
]