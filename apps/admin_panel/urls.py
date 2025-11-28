# apps/admin_panel/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView  # 👈
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.users, name='users'),
    path('groups/', views.groups, name='groups'),
    path('students/', views.students, name='students'),
    path('subjects/', views.subjects, name='subjects'),
    path('excel-import/', views.excel_import, name='excel_import'),
    path('logout/', LogoutView.as_view(), name='logout'),  # ← added here
]