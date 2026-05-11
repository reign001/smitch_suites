from django.urls import path
from . import views

app_name = 'reception'

urlpatterns = [
    path('dashboard/', views.reception_dashboard, name='dashboard'),

    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/create/', views.create_booking, name='create_booking'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:booking_id>/pdf/', views.download_booking_pdf, name='download_booking_pdf'),
    path('check-in/', views.check_in_guest, name='check_in_guest'),
    path('check-in/<int:booking_id>/', views.process_check_in, name='process_check_in'),
    path('check-in/', views.check_in_guest, name='check_in_guest'),
    path('guests/pdf/', views.download_guest_list_pdf, name='download_guest_list_pdf'),
    path('check-out/', views.check_out_guest, name='check_out_guest'),
    path('check-out/<int:booking_id>/', views.process_check_out, name='process_check_out'),
    path('check-out/<int:booking_id>/pdf/', views.download_checkout_pdf, name='download_checkout_pdf'),
    path('check-out/', views.check_out_guest, name='check_out_guest'),

    path('rooms/', views.room_list, name='room_list'),
    path('rooms/pdf/', views.download_rooms_pdf, name='download_rooms_pdf'),
    path('rooms/<int:room_id>/mark-clean/', views.mark_room_clean, name='mark_room_clean'),
    path('room-service/', views.room_service_list, name='room_service_list'),
    path('room-service/create/', views.create_room_service, name='create_room_service'),
    path('room-service/<int:service_id>/complete/', views.complete_room_service, name='complete_room_service'),
    path('room-service/<int:service_id>/cancel/', views.cancel_room_service, name='cancel_room_service'),
    path('guests/', views.guest_list, name='guest_list'),
    path('reports/', views.reports_center, name='reports_center'),
    path('reports/pdf/', views.download_reception_report_pdf, name='download_reception_report_pdf'),
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reports/finance/', views.finance_report, name='finance_report'),
    path('reports/finance/', views.finance_report, name='finance_report'),
    path('reports/finance/pdf/', views.download_finance_report_pdf, name='download_finance_report_pdf'),
]