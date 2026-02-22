from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'is_present', 'point', 'is_locked')
    list_filter = ('course', 'date', 'is_present', 'is_locked')
    search_fields = ('student__student__username', 'student__student__first_name', 'student__student__last_name', 'course__title')
    list_editable = ('is_locked',)
