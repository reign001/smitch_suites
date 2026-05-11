from django.urls import path
from . import views

app_name = 'bar'

urlpatterns = [
    path('', views.bar_dashboard, name='dashboard'),
    path('items/', views.bar_item_list, name='bar_item_list'),
    path('items/add/', views.add_bar_item, name='add_bar_item'),

    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.create_sale, name='create_sale'),
    path('sales/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:sale_id>/add-to-room/', views.add_sale_to_room_bill, name='add_sale_to_room_bill'),

    path('reports/', views.bar_report, name='bar_report'),
    path('reports/pdf/', views.download_bar_report_pdf, name='download_bar_report_pdf'),
]