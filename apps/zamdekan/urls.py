from django.urls import path
from . import views

app_name = 'zamdekan'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('live/', views.live_dashboard, name='live_dashboard'),
    path('students/', views.students_list, name='students'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('journals/', views.journals_list, name='journals'),
]
