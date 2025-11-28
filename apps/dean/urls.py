from django.urls import path
from . import views

app_name = 'dean'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('live/', views.live_dashboard, name='live_dashboard'),
    path('students/', views.students_list, name='students'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('groups/', views.groups_list, name='groups'),
    path('teachers/', views.teachers_list, name='teachers'),
    path('journals/', views.journals_list, name='journals'),
    path('reports/', views.reports, name='reports'),
    path('reports/export-pdf/', views.export_pdf, name='export_pdf'),
    path('api/live-data/', views.live_data_api, name='live_data_api'),
    
    # Admin functions inside dean
    path('users/', views.users_management, name='users'),
    path('users/create/', views.create_user, name='create_user'),
]
