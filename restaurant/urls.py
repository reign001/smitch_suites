from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.restaurant_dashboard, name='dashboard'),
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/add/', views.add_menu_item, name='add_menu_item'),

    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/add-to-room/', views.add_order_to_room_bill, name='add_order_to_room_bill'),

    path('reports/', views.restaurant_report, name='restaurant_report'),
    path('reports/pdf/', views.download_restaurant_report_pdf, name='download_restaurant_report_pdf'),
]