from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('', views.report_dashboard, name='dashboard'),
    path('generate/', views.generate_report, name='generate_report'),
    path('download/pdf/', views.download_report_pdf, name='download_report_pdf'),
]