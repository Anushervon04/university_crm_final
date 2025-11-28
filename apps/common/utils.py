import openpyxl
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

from django.template.loader import render_to_string
from .models import JournalEntry, Student, CurrentLesson


def import_journal_from_excel(file_path, teacher_assignment):
    """Импорт журнала из Excel"""
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    
    results = {'success': 0, 'errors': []}
    
    for row in ws.iter_rows(min_row=2, values_only=True):
        try:
            student_id, date_str, grade, attendance = row[:4]
            
            # Найти студента
            student = Student.objects.get(student_id=student_id)
            
            # Преобразовать дату
            if isinstance(date_str, str):
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                date = date_str
            
            # Создать или обновить запись
            entry, created = JournalEntry.objects.update_or_create(
                student=student,
                teacher_assignment=teacher_assignment,
                date=date,
                defaults={
                    'grade': int(grade) if grade else None,
                    'attendance': bool(attendance),
                }
            )
            results['success'] += 1
        except Exception as e:
            results['errors'].append(f"Row error: {str(e)}")
    
    return results


# -----------------------------
#   НОВЫЙ PDF БЕЗ WEASYPRINT
# -----------------------------
def export_report_to_pdf(title, rows):
    """Создание PDF отчета без WeasyPrint — 100% работает в Windows"""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    y = 800
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, title)
    y -= 40

    pdf.setFont("Helvetica", 12)
    for row in rows:
        pdf.drawString(50, y, str(row))
        y -= 20
        if y < 50:
            pdf.showPage()
            y = 800

    pdf.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type="application/pdf")


def calculate_weekly_attendance_points(student, teacher_assignment, week_start_date):
    """Расчет баллов посещаемости за неделю"""
    week_end = week_start_date + timedelta(days=7)
    
    entries = JournalEntry.objects.filter(
        student=student,
        teacher_assignment=teacher_assignment,
        date__gte=week_start_date,
        date__lt=week_end,
        attendance=True
    )
    
    days_attended = entries.count()
    
    if days_attended >= 3:
        return 6.0
    else:
        return days_attended * 1.6


def get_live_attendance_data():
    """Данные Live Dashboard"""
    now = timezone.now()
    current_date = now.date()
    current_time = now.time()
    
    current_lessons = CurrentLesson.objects.filter(
        date=current_date,
        schedule__start_time__lte=current_time,
        schedule__end_time__gte=current_time
    ).select_related(
        'schedule__teacher_assignment__teacher',
        'schedule__teacher_assignment__group',
        'schedule__teacher_assignment__subject'
    )
    
    data = {
        'current_lessons': [],
        'total_present': 0,
        'total_students': 0,
    }
    
    for lesson in current_lessons:
        ta = lesson.schedule.teacher_assignment
        data['current_lessons'].append({
            'group': ta.group.name,
            'subject': ta.subject.name,
            'teacher': ta.teacher.full_name,
            'room': lesson.schedule.room,
            'present': lesson.present_count,
            'total': lesson.total_students,
            'percentage': lesson.attendance_percentage(),
        })
        data['total_present'] += lesson.present_count
        data['total_students'] += lesson.total_students
    
    if data['total_students'] > 0:
        data['overall_percentage'] = round((data['total_present'] / data['total_students']) * 100, 1)
    else:
        data['overall_percentage'] = 0
    
    return data


def get_top_students(limit=10):
    """Топ студентов по GPA"""
    return Student.objects.filter(is_active=True).order_by('-gpa')[:limit]


def get_debt_students():
    """Студенты с долгами"""
    return Student.objects.filter(contract_status='debt', is_active=True).order_by('last_name')
