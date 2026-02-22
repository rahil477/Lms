from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.attendance_course_list, name='attendance_course_list'),
    path('course/<int:course_id>/take/', views.take_attendance, name='take_attendance'),
    path('my-attendance/', views.student_attendance_report, name='student_attendance_report'),
]
