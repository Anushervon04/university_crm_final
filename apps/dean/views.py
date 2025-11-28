from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from apps.common.models import *
from apps.common.permissions import dean_required
from apps.common.utils import get_live_attendance_data, get_top_students, get_debt_students, export_report_to_pdf
from django.db.models import Count, Avg


@dean_required
def dashboard(request):
    """Главная панель декана"""
    total_students = Student.objects.filter(is_active=True).count()
    total_groups = Group.objects.count()
    total_teachers = User.objects.filter(role='teacher').count()
    avg_gpa = Student.objects.filter(is_active=True).aggregate(Avg('gpa'))['gpa__avg'] or 0
    
    # Статистика посещаемости сегодня
    today = timezone.now().date()
    today_entries = JournalEntry.objects.filter(date=today)
    today_present = today_entries.filter(attendance=True).count()
    today_total = today_entries.count()
    today_percentage = round((today_present / today_total * 100), 1) if today_total > 0 else 0
    
    context = {
        'total_students': total_students,
        'total_groups': total_groups,
        'total_teachers': total_teachers,
        'avg_gpa': round(avg_gpa, 2),
        'today_percentage': today_percentage,
        'top_students': get_top_students(10),
        'debt_students': get_debt_students()[:10],
    }
    return render(request, 'dean/dashboard.html', context)


@dean_required
def live_dashboard(request):
    """Live Dashboard с автообновлением каждые 15 секунд"""
    live_data = get_live_attendance_data()
    return render(request, 'dean/live_dashboard.html', {'live_data': live_data})


@dean_required
def live_data_api(request):
    """API для получения live данных (AJAX)"""
    data = get_live_attendance_data()
    return JsonResponse(data, safe=False)


@dean_required
def students_list(request):
    """Список всех студентов с поиском и фильтрацией"""
    students = Student.objects.filter(is_active=True).select_related('group', 'course')
    
    # Поиск
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) | 
            Q(student_id__icontains=search)
        )
    
    # Фильтр по группе
    group_id = request.GET.get('group')
    if group_id:
        students = students.filter(group_id=group_id)
    
    groups = Group.objects.all()
    
    return render(request, 'dean/students.html', {
        'students': students,
        'groups': groups,
        'search': search
    })


@dean_required
def student_detail(request, pk):
    """Профиль студента"""
    student = get_object_or_404(Student, pk=pk)
    journal_entries = JournalEntry.objects.filter(student=student).select_related(
        'teacher_assignment__subject', 'teacher_assignment__teacher'
    ).order_by('-date')[:20]
    comments = Comment.objects.filter(student=student).select_related('author').order_by('-created_at')
    
    return render(request, 'dean/student_detail.html', {
        'student': student,
        'journal_entries': journal_entries,
        'comments': comments
    })


@dean_required
def groups_list(request):
    """Список групп"""
    groups = Group.objects.all().select_related('course').annotate(
        student_count=Count('students')
    )
    return render(request, 'dean/groups.html', {'groups': groups})


@dean_required
def teachers_list(request):
    """Список учителей"""
    teachers = User.objects.filter(role='teacher')
    return render(request, 'dean/teachers.html', {'teachers': teachers})


@dean_required
def journals_list(request):
    """Журналы"""
    assignments = TeacherAssignment.objects.all().select_related(
        'teacher', 'group', 'subject', 'semester'
    )
    return render(request, 'dean/journals.html', {'assignments': assignments})


@dean_required
def reports(request):
    """Отчеты"""
    return render(request, 'dean/reports.html')


@dean_required
def export_pdf(request):
    """Экспорт отчета в PDF"""
    students = Student.objects.filter(is_active=True)
    context = {'students': students, 'title': 'Рӯйхати донишҷӯён'}
    pdf = export_report_to_pdf("report.html", context)

    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response


@dean_required
def users_management(request):
    """Управление пользователями (админ функция внутри декана)"""
    users = User.objects.all()
    return render(request, 'dean/users.html', {'users': users})


@dean_required
def create_user(request):
    """Создание пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        full_name = request.POST.get('full_name')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role,
            full_name=full_name
        )
        messages.success(request, f'Корбар {username} эҷод шуд!')
        return redirect('dean:users')
    
    return render(request, 'dean/create_user.html')
