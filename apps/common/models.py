from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta


class User(AbstractUser):
    """Корбар (Декан, Админ, Замдекан, Омӯзгор)"""
    ROLE_CHOICES = [
        ('dean', 'Декан'),
        ('admin', 'Админ'),
        ('zamdekan', 'Замдекан'),
        ('teacher', 'Омӯзгор'),
    ]
    role = models.CharField('Нақш', max_length=20, choices=ROLE_CHOICES)
    full_name = models.CharField('Номи пурра', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    photo = models.ImageField('Сурат', upload_to='users/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Корбар'
        verbose_name_plural = 'Корбарон'
    
    def __str__(self):
        return f"{self.full_name or self.username} ({self.get_role_display()})"


class Course(models.Model):
    """Курс (1, 2, 3, 4)"""
    number = models.IntegerField('Рақами курс', unique=True)
    name = models.CharField('Номи курс', max_length=100)
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсҳо'
        ordering = ['number']
    
    def __str__(self):
        return f"Курси {self.number}"


class Group(models.Model):
    """Гурӯҳ"""
    name = models.CharField('Номи гурӯҳ', max_length=100, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс', related_name='groups')
    created_at = models.DateTimeField('Сана', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Гурӯҳ'
        verbose_name_plural = 'Гурӯҳҳо'
        ordering = ['course', 'name']
    
    def __str__(self):
        return self.name


class Subject(models.Model):
    """Фан"""
    name = models.CharField('Номи фан', max_length=200)
    code = models.CharField('Коди фан', max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс', related_name='subjects')
    hours_per_week = models.IntegerField('Соатҳо дар ҳафта', default=3)
    
    class Meta:
        verbose_name = 'Фан'
        verbose_name_plural = 'Фанҳо'
        ordering = ['course', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Student(models.Model):
    """Донишҷӯ"""
    student_id = models.CharField('Рақами донишҷӯӣ', max_length=50, unique=True)
    first_name = models.CharField('Ном', max_length=100)
    last_name = models.CharField('Насаб', max_length=100)
    middle_name = models.CharField('Номи падар', max_length=100, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, verbose_name='Гурӯҳ', related_name='students')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, verbose_name='Курс')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    photo = models.ImageField('Сурат', upload_to='students/', blank=True, null=True)
    enrollment_date = models.DateField('Санаи қабул', default=timezone.now)
    gpa = models.DecimalField('GPA', max_digits=3, decimal_places=2, default=0.00)
    contract_status = models.CharField('Ҳолати шартнома', max_length=20, 
                                      choices=[('paid', 'Пардохт'), ('debt', 'Қарз')], 
                                      default='paid')
    is_active = models.BooleanField('Фаъол', default=True)
    
    class Meta:
        verbose_name = 'Донишҷӯ'
        verbose_name_plural = 'Донишҷӯён'
        ordering = ['group', 'last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.student_id})"
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"


class Semester(models.Model):
    """Семестр"""
    name = models.CharField('Номи семестр', max_length=100)
    start_date = models.DateField('Санаи оғоз')
    end_date = models.DateField('Санаи анҷом')
    is_active = models.BooleanField('Фаъол', default=True)
    
    class Meta:
        verbose_name = 'Семестр'
        verbose_name_plural = 'Семестрҳо'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name


class TeacherAssignment(models.Model):
    """Таъин кардани омӯзгор ба гурӯҳ ва фан"""
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, 
                                verbose_name='Омӯзгор', related_name='assignments')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Гурӯҳ')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Фан')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, verbose_name='Семестр')
    can_grade = models.BooleanField('Ҳуқуқи баҳогузорӣ', default=True)
    
    class Meta:
        verbose_name = 'Таъинот'
        verbose_name_plural = 'Таъинотҳо'
        unique_together = ['teacher', 'group', 'subject', 'semester']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.subject.name} - {self.group.name}"


class Schedule(models.Model):
    """Расписание (Ҷадвали дарсҳо)"""
    WEEKDAY_CHOICES = [
        (0, 'Душанбе'),
        (1, 'Сешанбе'),
        (2, 'Чоршанбе'),
        (3, 'Панҷшанбе'),
        (4, 'Ҷумъа'),
        (5, 'Шанбе'),
    ]
    
    teacher_assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, 
                                          verbose_name='Таъинот', related_name='schedules')
    weekday = models.IntegerField('Рӯзи ҳафта', choices=WEEKDAY_CHOICES)
    start_time = models.TimeField('Вақти оғоз')
    end_time = models.TimeField('Вақти анҷом')
    room = models.CharField('Толор', max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписанияҳо'
        ordering = ['weekday', 'start_time']
    
    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time}-{self.end_time} - {self.teacher_assignment}"
    
    def is_locked(self):
        """Блокировка через 1 час после окончания урока"""
        now = timezone.now()
        lesson_end = datetime.combine(now.date(), self.end_time)
        lesson_end = timezone.make_aware(lesson_end)
        return now > (lesson_end + timedelta(hours=1))


class JournalEntry(models.Model):
    """Журнал (Оценки и посещаемость)"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Донишҷӯ', related_name='journal_entries')
    teacher_assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, verbose_name='Таъинот')
    date = models.DateField('Сана')
    grade = models.IntegerField('Баҳо', choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3')], null=True, blank=True)
    attendance = models.BooleanField('Ҳозиршавӣ', default=False)
    attendance_points = models.DecimalField('Баллҳои ҳозиршавӣ', max_digits=4, decimal_places=2, default=0.00)
    created_at = models.DateTimeField('Сана', auto_now_add=True)
    updated_at = models.DateTimeField('Навсозӣ', auto_now=True)
    
    class Meta:
        verbose_name = 'Ёддошти журнал'
        verbose_name_plural = 'Ёддоштҳои журнал'
        unique_together = ['student', 'teacher_assignment', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.teacher_assignment.subject.name} - {self.date}"
    
    def save(self, *args, **kwargs):
        """Автоматический расчет баллов посещаемости"""
        if self.attendance:
            # +1.6 балла за каждый день
            self.attendance_points = 1.6
            
            # Проверка: если 3 дня в неделю = автоматом +6 баллов
            week_start = self.date - timedelta(days=self.date.weekday())
            week_entries = JournalEntry.objects.filter(
                student=self.student,
                teacher_assignment=self.teacher_assignment,
                date__gte=week_start,
                date__lt=week_start + timedelta(days=7),
                attendance=True
            ).count()
            
            if week_entries >= 3:
                self.attendance_points = 6.0 / week_entries
        else:
            self.attendance_points = 0.0
        
        super().save(*args, **kwargs)


class Comment(models.Model):
    """Комментарии о поведении студента"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Донишҷӯ', related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Муаллиф')
    text = models.TextField('Матн')
    comment_type = models.CharField('Навъ', max_length=20, 
                                   choices=[('positive', 'Мусбат'), ('negative', 'Манфӣ'), ('neutral', 'Хунук')],
                                   default='neutral')
    created_at = models.DateTimeField('Сана', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Коммент'
        verbose_name_plural = 'Комментҳо'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.full_name} → {self.student} ({self.created_at.date()})"


class CurrentLesson(models.Model):
    """Текущий урок (для live dashboard)"""
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='Расписание')
    date = models.DateField('Сана', default=timezone.now)
    present_count = models.IntegerField('Ҳозирон', default=0)
    total_students = models.IntegerField('Ҷамъи донишҷӯён', default=0)
    
    class Meta:
        verbose_name = 'Дарси ҷорӣ'
        verbose_name_plural = 'Дарсҳои ҷорӣ'
        unique_together = ['schedule', 'date']
    
    def __str__(self):
        return f"{self.schedule} - {self.date}"
    
    def attendance_percentage(self):
        if self.total_students == 0:
            return 0
        return round((self.present_count / self.total_students) * 100, 1)
