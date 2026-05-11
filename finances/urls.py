from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    path('', views.finance_dashboard, name='dashboard'),

    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.create_expense, name='create_expense'),

    path('transactions/', views.transaction_list, name='transaction_list'),

    path('daily-report/', views.daily_finance_report, name='daily_finance_report'),
    path('daily-report/pdf/', views.download_daily_finance_report_pdf, name='download_daily_finance_report_pdf'),
]