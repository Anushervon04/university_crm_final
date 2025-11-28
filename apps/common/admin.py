from django.contrib import admin
from .models import (User, Course, Group, Subject, Student, Semester, 
                    TeacherAssignment, Schedule, JournalEntry, Comment, CurrentLesson)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'full_name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['number', 'name']
    ordering = ['number']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'created_at']
    list_filter = ['course']
    search_fields = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'course', 'hours_per_week']
    list_filter = ['course']
    search_fields = ['name', 'code']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'last_name', 'first_name', 'group', 'course', 'gpa', 'contract_status', 'is_active']
    list_filter = ['group', 'course', 'contract_status', 'is_active']
    search_fields = ['student_id', 'last_name', 'first_name']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'group', 'subject', 'semester', 'can_grade']
    list_filter = ['semester', 'can_grade']
    search_fields = ['teacher__full_name', 'group__name', 'subject__name']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher_assignment', 'weekday', 'start_time', 'end_time', 'room']
    list_filter = ['weekday']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['student', 'teacher_assignment', 'date', 'grade', 'attendance', 'attendance_points']
    list_filter = ['date', 'attendance']
    search_fields = ['student__last_name', 'student__first_name']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['student', 'author', 'comment_type', 'created_at']
    list_filter = ['comment_type', 'created_at']
    search_fields = ['student__last_name', 'author__full_name']


@admin.register(CurrentLesson)
class CurrentLessonAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'date', 'present_count', 'total_students', 'attendance_percentage']
    list_filter = ['date']
