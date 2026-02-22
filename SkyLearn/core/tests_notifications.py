from django.test import TestCase
from django.contrib.auth import get_user_model
from course.models import Course, Program, Upload
from quiz.models import Quiz
from result.models import TakenCourse
from core.models import Notification, Semester
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class NotificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', password='password')
        self.lecturer = User.objects.create_user(username='lecturer1', password='password', is_lecturer=True)
        self.program = Program.objects.create(title='CS')
        self.semester = Semester.objects.create(semester='First', is_current_semester=True)
        self.course = Course.objects.create(
            title='Intro to AI',
            code='CS101',
            program=self.program,
            semester='First'
        )
        # Enroll student
        self.student_profile = self.user # In this system, Student is a separate model often, let's check
        from accounts.models import Student
        self.student = Student.objects.create(student=self.user, program=self.program, level='Bachelor')
        TakenCourse.objects.create(student=self.student, course=self.course)

    def test_upload_triggers_notification(self):
        file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        Upload.objects.create(title="Test Note", course=self.course, file=file)
        
        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(notifications.count(), 1)
        self.assertIn("Yeni sənəd əlavə edildi", notifications.first().verb)

    def test_quiz_triggers_notification(self):
        Quiz.objects.create(title="Test Quiz", course=self.course)
        
        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(notifications.count(), 1)
        self.assertIn("Yeni test imtahanı əlavə edildi", notifications.first().verb)
