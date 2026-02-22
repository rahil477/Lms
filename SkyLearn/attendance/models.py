from django.db import models
from django.conf import settings
from course.models import Course
from accounts.models import Student

class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    point = models.IntegerField(default=0, help_text="10-point grading system")
    note = models.TextField(blank=True, null=True)
    is_locked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['course', 'student', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.course} - {self.date}"

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg

@receiver(post_save, sender=Attendance)
@receiver(post_delete, sender=Attendance)
def update_taken_course_attendance(sender, instance, **kwargs):
    from result.models import TakenCourse
    taken_course = TakenCourse.objects.filter(
        student=instance.student, course=instance.course
    ).first()
    
    if taken_course:
        attendances = Attendance.objects.filter(
            student=instance.student, course=instance.course
        )
        
        avg_point = attendances.aggregate(Avg('point'))['point__avg'] or 0
        taken_course.attendance = avg_point
        taken_course.save()
        
        # Calculate percentage to notify if it drops below 75%
        total_days = attendances.count()
        if total_days > 0:
            present_count = attendances.filter(is_present=True).count()
            percentage = (present_count / total_days) * 100
            
            if percentage < 75.0:
                from core.models import Notification
                from django.utils.translation import gettext_lazy as _
                
                # Notify student
                Notification.objects.get_or_create(
                    user=instance.student.student,
                    verb=_("Kritik Davamiyyət Xəbərdarlığı"),
                    description=f"Diqqət! {instance.course.title} fənni üzrə davamiyyətiniz {percentage:.1f}% səviyyəsinə düşüb (Kritik hədd: 75%)."
                )
                
                # Notify course lecturers
                from course.models import CourseAllocation
                allocations = CourseAllocation.objects.filter(courses=instance.course)
                for allocation in allocations:
                    Notification.objects.get_or_create(
                        user=allocation.lecturer,
                        verb=_("Tələbə Davamiyyət Xəbərdarlığı"),
                        description=f"{instance.student.student.get_full_name()} adlı tələbənin {instance.course.title} fənni üzrə davamiyyəti {percentage:.1f}%-ə (Kritik hədd: 75%) düşmüşdür."
                    )
