from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.common.models import *
from apps.common.permissions import zamdekan_required
from apps.common.utils import get_live_attendance_data, get_top_students
from django.db.models import Count


@zamdekan_required
def dashboard(request):
    """Панель замдекана (только просмотр)"""
    total_students = Student.objects.filter(is_active=True).count()
    total_groups = Group.objects.count()
    
    context = {
        'total_students': total_students,
        'total_groups': total_groups,
        'top_students': get_top_students(10),
    }
    return render(request, 'zamdekan/dashboard.html', context)


@zamdekan_required
def live_dashboard(request):
    """Live Dashboard (только просмотр)"""
    live_data = get_live_attendance_data()
    return render(request, 'zamdekan/live_dashboard.html', {'live_data': live_data})


@zamdekan_required
def students_list(request):
    """Список студентов (только просмотр)"""
    students = Student.objects.filter(is_active=True).select_related('group', 'course')
    
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) | 
            Q(student_id__icontains=search)
        )
    
    return render(request, 'zamdekan/students.html', {'students': students, 'search': search})


@zamdekan_required
def student_detail(request, pk):
    """Профиль студента (только просмотр + комментарии)"""
    student = get_object_or_404(Student, pk=pk)
    journal_entries = JournalEntry.objects.filter(student=student).select_related(
        'teacher_assignment__subject', 'teacher_assignment__teacher'
    ).order_by('-date')[:20]
    comments = Comment.objects.filter(student=student).select_related('author').order_by('-created_at')
    
    return render(request, 'zamdekan/student_detail.html', {
        'student': student,
        'journal_entries': journal_entries,
        'comments': comments
    })


@zamdekan_required
def add_comment(request, pk):
    """Добавить комментарий студенту"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        comment_type = request.POST.get('comment_type', 'neutral')
        
        Comment.objects.create(
            student=student,
            author=request.user,
            text=text,
            comment_type=comment_type
        )
        messages.success(request, 'Коммент илова шуд!')
        return redirect('zamdekan:student_detail', pk=pk)
    
    return render(request, 'zamdekan/add_comment.html', {'student': student})


@zamdekan_required
def journals_list(request):
    """Журналы (только просмотр)"""
    assignments = TeacherAssignment.objects.all().select_related(
        'teacher', 'group', 'subject', 'semester'
    )
    return render(request, 'zamdekan/journals.html', {'assignments': assignments})
