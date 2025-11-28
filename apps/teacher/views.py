from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from apps.common.models import *
from apps.common.permissions import teacher_required
from django.utils import timezone


@teacher_required
def dashboard(request):
    """Панель учителя"""
    my_assignments = TeacherAssignment.objects.filter(
        teacher=request.user,
        semester__is_active=True
    ).select_related('group', 'subject')
    
    my_schedules = Schedule.objects.filter(
        teacher_assignment__teacher=request.user
    ).select_related('teacher_assignment__group', 'teacher_assignment__subject')
    
    return render(request, 'teacher/dashboard.html', {
        'assignments': my_assignments,
        'schedules': my_schedules
    })


@teacher_required
def my_schedule(request):
    """Мое расписание"""
    schedules = Schedule.objects.filter(
        teacher_assignment__teacher=request.user
    ).select_related(
        'teacher_assignment__group',
        'teacher_assignment__subject'
    ).order_by('weekday', 'start_time')
    
    return render(request, 'teacher/schedule.html', {'schedules': schedules})


@teacher_required
def my_groups(request):
    """Мои группы"""
    assignments = TeacherAssignment.objects.filter(
        teacher=request.user,
        semester__is_active=True
    ).select_related('group', 'subject')
    
    return render(request, 'teacher/groups.html', {'assignments': assignments})


@teacher_required
def journal(request, assignment_id):
    """Журнал группы"""
    assignment = get_object_or_404(
        TeacherAssignment,
        id=assignment_id,
        teacher=request.user
    )
    
    students = Student.objects.filter(
        group=assignment.group,
        is_active=True
    ).order_by('last_name', 'first_name')
    
    # Получить записи журнала за последние 30 дней
    from datetime import timedelta
    today = timezone.now().date()
    start_date = today - timedelta(days=30)
    
    entries = JournalEntry.objects.filter(
        teacher_assignment=assignment,
        date__gte=start_date
    ).select_related('student')
    
    # Организовать по студентам и датам
    journal_data = {}
    for student in students:
        student_entries = entries.filter(student=student).order_by('-date')
        journal_data[student.id] = {
            'student': student,
            'entries': student_entries
        }
    
    return render(request, 'teacher/journal.html', {
        'assignment': assignment,
        'journal_data': journal_data,
        'students': students
    })


@teacher_required
def update_grade(request, assignment_id):
    """Обновить оценку/посещаемость"""
    if request.method == 'POST':
        assignment = get_object_or_404(
            TeacherAssignment,
            id=assignment_id,
            teacher=request.user
        )
        
        student_id = request.POST.get('student_id')
        date_str = request.POST.get('date')
        grade = request.POST.get('grade')
        attendance = request.POST.get('attendance') == 'true'
        
        student = Student.objects.get(id=student_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Проверить блокировку
        schedule = Schedule.objects.filter(
            teacher_assignment=assignment,
            weekday=date.weekday()
        ).first()
        
        if schedule and schedule.is_locked():
            return JsonResponse({
                'status': 'error',
                'message': 'Ячейка қулф шудааст (1 соат гузашт)!'
            })
        
        # Создать или обновить запись
        entry, created = JournalEntry.objects.update_or_create(
            student=student,
            teacher_assignment=assignment,
            date=date,
            defaults={
                'grade': int(grade) if grade else None,
                'attendance': attendance
            }
        )
        
        messages.success(request, 'Баҳо навсозӣ шуд!')
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'})


@teacher_required
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
        return redirect('teacher:dashboard')
    
    return render(request, 'teacher/add_comment.html', {'student': student})
