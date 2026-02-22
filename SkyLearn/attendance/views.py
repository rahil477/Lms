from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Attendance
from course.models import Course, CourseAllocation
from accounts.models import Student
from result.models import TakenCourse
from accounts.decorators import lecturer_required, student_required

@login_required
@lecturer_required
def attendance_course_list(request):
    """List of courses allocated to the lecturer to take attendance."""
    allocations = CourseAllocation.objects.filter(lecturer=request.user)
    courses = []
    for allocation in allocations:
        for course in allocation.courses.all():
            courses.append(course)
    
    return render(request, 'attendance/attendance_course_list.html', {'courses': courses})

@login_required
@lecturer_required
def take_attendance(request, course_id):
    """View to take attendance for a specific course."""
    course = get_object_or_404(Course, pk=course_id)
    # Check if the lecturer is allowed to take attendance for this course
    if not CourseAllocation.objects.filter(lecturer=request.user, courses=course).exists():
        messages.error(request, "Sizin bu kurs üçün davamiyyət götürmək səlahiyyətiniz yoxdur.")
        return redirect('attendance_course_list')

    students = Student.objects.filter(taken_courses__course=course)
    date = request.GET.get('date', timezone.now().date().isoformat())

    if request.method == 'POST':
        # Check if already locked and user is not admin
        is_already_locked = Attendance.objects.filter(course=course, date=request.POST.get('date'), is_locked=True).exists()
        if is_already_locked and not request.user.is_superuser:
            messages.error(request, "Bu tarix üçün jurnal kilidləndiyinə görə dəyişiklik etmək mümkün deyil.")
            return redirect('attendance_course_list')

        date = request.POST.get('date')
        lock_immediately = request.POST.get('lock_journal') == 'on'
        
        for student in students:
            status = request.POST.get(f'student_{student.id}')
            is_present = True if status == 'present' else False
            point = request.POST.get(f'point_{student.id}', 0)
            note = request.POST.get(f'note_{student.id}', '')
            
            try:
                point = int(point)
                if point < 0: point = 0
                if point > 10: point = 10
            except (ValueError, TypeError):
                point = 0

            Attendance.objects.update_or_create(
                course=course,
                student=student,
                date=date,
                defaults={
                    'is_present': is_present,
                    'point': point,
                    'note': note,
                    'is_locked': lock_immediately
                }
            )
        
        if lock_immediately:
            messages.success(request, f"{date} tarixi üçün jurnal təsdiqləndi və kilidləndi.")
            
            # Notify students
            from core.models import Notification
            from django.utils.translation import gettext_lazy as _
            notifications = []
            for student in students:
                notifications.append(
                    Notification(
                        user=student.student,
                        verb=_("E-Jurnal təsdiqləndi"),
                        description=f"{course.title} fənni üzrə {date} tarixli jurnala qeydləriniz yazıldı.",
                        target_url=request.path
                    )
                )
            if notifications:
                Notification.objects.bulk_create(notifications)
        else:
            messages.success(request, f"{date} tarixi üçün jurnal yadda saxlanıldı.")
        return redirect('attendance_course_list')

    # Get existing attendance for this date if any
    existing_attendance = Attendance.objects.filter(course=course, date=date)
    attendance_dict = {a.student_id: a.is_present for a in existing_attendance}
    points_dict = {a.student_id: a.point for a in existing_attendance}
    notes_dict = {a.student_id: a.note for a in existing_attendance}
    is_locked = any(a.is_locked for a in existing_attendance)

    return render(request, 'attendance/take_attendance.html', {
        'course': course,
        'students': students,
        'date': date,
        'attendance_dict': attendance_dict,
        'points_dict': points_dict,
        'notes_dict': notes_dict,
        'is_locked': is_locked
    })

@login_required
@student_required
def student_attendance_report(request):
    """View for students to see their attendance across all courses."""
    student = get_object_or_404(Student, student=request.user)
    taken_courses = TakenCourse.objects.filter(student=student)
    
    report = []
    for tc in taken_courses:
        course = tc.course
        attendances = Attendance.objects.filter(course=course, student=student)
        total_days = attendances.count()
        present_count = attendances.filter(is_present=True).count()
        absent_count = total_days - present_count
        percentage = (present_count / total_days * 100) if total_days > 0 else 0
        
        report.append({
            'course': course,
            'total_days': total_days,
            'present_count': present_count,
            'absent_count': absent_count,
            'percentage': round(percentage, 2)
        })

    return render(request, 'attendance/student_attendance_report.html', {'report': report})
