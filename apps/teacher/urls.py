from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('schedule/', views.my_schedule, name='schedule'),
    path('groups/', views.my_groups, name='groups'),
    path('journal/<int:assignment_id>/', views.journal, name='journal'),
    path('journal/<int:assignment_id>/update/', views.update_grade, name='update_grade'),
    path('student/<int:pk>/comment/', views.add_comment, name='add_comment'),
]
