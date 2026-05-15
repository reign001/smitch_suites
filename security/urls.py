from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('', views.security_dashboard, name='dashboard'),

    path('visitors/', views.visitor_list, name='visitor_list'),
    path('visitors/create/', views.create_visitor_log, name='create_visitor_log'),
    path('visitors/<int:visitor_id>/checkout/', views.checkout_visitor, name='checkout_visitor'),

    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/create/', views.create_incident, name='create_incident'),

    path('blacklist/', views.blacklist_list, name='blacklist_list'),
    path('blacklist/create/', views.create_blacklist_record, name='create_blacklist_record'),

    path('keys/', views.keycard_list, name='keycard_list'),
    path('keys/create/', views.create_keycard_log, name='create_keycard_log'),

    path('patrols/', views.patrol_list, name='patrol_list'),
    path('patrols/create/', views.create_patrol_log, name='create_patrol_log'),

    path('reports/', views.security_report, name='security_report'),
    path('reports/pdf/', views.download_security_report_pdf, name='download_security_report_pdf'),
]