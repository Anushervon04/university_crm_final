from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common.models import *
from apps.common.permissions import admin_required
from apps.common.utils import import_journal_from_excel


@admin_required
def dashboard(request):
    """Админ панель"""
    total_users = User.objects.count()
    total_students = Student.objects.count()
    total_groups = Group.objects.count()
    
    return render(request, 'admin_panel/dashboard.html', {
        'total_users': total_users,
        'total_students': total_students,
        'total_groups': total_groups
    })


@admin_required
def users(request):
    """Управление пользователями"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            username = request.POST.get('username')
            password = request.POST.get('password')
            role = request.POST.get('role')
            full_name = request.POST.get('full_name')
            
            User.objects.create_user(
                username=username,
                password=password,
                role=role,
                full_name=full_name
            )
            messages.success(request, 'Корбар эҷод шуд!')
            return redirect('admin_panel:users')
    
    all_users = User.objects.all()
    return render(request, 'admin_panel/users.html', {'users': all_users})


@admin_required
def groups(request):
    """Управление группами"""
    if request.method == 'POST':
        name = request.POST.get('name')
        course_id = request.POST.get('course_id')
        
        Group.objects.create(name=name, course_id=course_id)
        messages.success(request, 'Гурӯҳ эҷод шуд!')
        return redirect('admin_panel:groups')
    
    all_groups = Group.objects.all().select_related('course')
    courses = Course.objects.all()
    return render(request, 'admin_panel/groups.html', {
        'groups': all_groups,
        'courses': courses
    })


@admin_required
def students(request):
    """Управление студентами"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        group_id = request.POST.get('group_id')
        
        group = Group.objects.get(id=group_id)
        Student.objects.create(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            group=group,
            course=group.course
        )
        messages.success(request, 'Донишҷӯ эҷод шуд!')
        return redirect('admin_panel:students')
    
    all_students = Student.objects.all().select_related('group', 'course')
    groups = Group.objects.all()
    return render(request, 'admin_panel/students.html', {
        'students': all_students,
        'groups': groups
    })


@admin_required
def subjects(request):
    """Управление предметами"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        course_id = request.POST.get('course_id')
        hours = request.POST.get('hours_per_week', 3)
        
        Subject.objects.create(
            name=name,
            code=code,
            course_id=course_id,
            hours_per_week=hours
        )
        messages.success(request, 'Фан эҷод шуд!')
        return redirect('admin_panel:subjects')
    
    all_subjects = Subject.objects.all().select_related('course')
    courses = Course.objects.all()
    return render(request, 'admin_panel/subjects.html', {
        'subjects': all_subjects,
        'courses': courses
    })


@admin_required
def excel_import(request):
    """Импорт журнала из Excel"""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        file = request.FILES['excel_file']
        assignment_id = request.POST.get('assignment_id')
        
        # Сохранить временно файл
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        # Импорт
        assignment = TeacherAssignment.objects.get(id=assignment_id)
        result = import_journal_from_excel(tmp_path, assignment)
        
        messages.success(request, f'Импорт: {result["success"]} қатор')
        if result['errors']:
            for error in result['errors']:
                messages.error(request, error)
        
        return redirect('admin_panel:excel_import')
    
    assignments = TeacherAssignment.objects.all().select_related('teacher', 'group', 'subject')
    return render(request, 'admin_panel/excel_import.html', {'assignments': assignments})
