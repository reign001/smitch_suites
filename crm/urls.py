from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.crm_dashboard, name='dashboard'),
    path('guests/', views.crm_guest_list, name='guest_list'),
    path('guests/<int:guest_id>/', views.guest_profile_detail, name='guest_detail'),

    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/create/', views.create_complaint, name='create_complaint'),

    path('feedback/create/', views.create_feedback, name='create_feedback'),

    path('corporate/', views.corporate_client_list, name='corporate_client_list'),
    path('corporate/create/', views.create_corporate_client, name='create_corporate_client'),
]