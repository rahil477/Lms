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
