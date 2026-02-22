from decimal import Decimal
from django.test import TestCase
from accounts.models import Student, User
from core.models import Semester, Session
from course.models import Course, Program
from result.models import TakenCourse, A_PLUS, F

class ResultCalculationTests(TestCase):
    def setUp(self):
        # Create user & student
        self.user = User.objects.create_user(
            username='student1', password='password', is_student=True
        )
        self.student = Student.objects.create(
            student=self.user, level='Bachelor'
        )
        
        # Create program, session, semester
        self.program = Program.objects.create(title='Computer Science')
        self.session = Session.objects.create(session='2025/2026', is_current_session=True)
        self.semester = Semester.objects.create(
            semester='First', is_current_semester=True, session=self.session
        )
        
        # Create course
        self.course = Course.objects.create(
            title='Intro to Programming',
            code='CS101',
            credit=3,
            level='Bachelor',
            year=1,
            semester='First',
            program=self.program
        )

    def test_get_total_and_get_grade(self):
        # Create taken course for student with perfect scores (100% in all metrics)
        taken_course = TakenCourse.objects.create(
            student=self.student,
            course=self.course,
            assignment=100.0,
            mid_exam=100.0,
            quiz=100.0,
            attendance=100.0,
            final_exam=100.0
        )
        
        # Test total
        self.assertEqual(taken_course.total, Decimal('100.00'))
        # Test grade
        self.assertEqual(taken_course.grade, A_PLUS)
        # Test comment
        self.assertEqual(taken_course.comment, 'PASS')
        # Test point (Credit 3 * A+ 4.0 = 12.0)
        self.assertEqual(taken_course.point, Decimal('12.0'))

    def test_failing_grade(self):
        # Student scores very low
        taken_course = TakenCourse.objects.create(
            student=self.student,
            course=self.course,
            assignment=0.0,
            mid_exam=20.0,
            quiz=10.0,
            attendance=50.0,
            final_exam=30.0
        )
        # Weights: Assign(15), Mid(20), Quiz(15), Att(10), Final(40)
        # Expected: (0*.15) + (20*.20) + (10*.15) + (50*.10) + (30*.40) = 0 + 4 + 1.5 + 5 + 12 = 22.5
        self.assertEqual(taken_course.total, Decimal('22.50'))
        # Test grade
        self.assertEqual(taken_course.grade, F)
        # Test comment
        self.assertEqual(taken_course.comment, 'FAIL')
        # Test point (Credit 3 * F 0.0 = 0.0)
        self.assertEqual(taken_course.point, Decimal('0.0'))

    def test_gpa_calculation(self):
        TakenCourse.objects.create(
            student=self.student,
            course=self.course,
            assignment=100.0,
            mid_exam=100.0,
            quiz=100.0,
            attendance=100.0,
            final_exam=100.0
        )
        
        course2 = Course.objects.create(
            title='Math',
            code='Math101',
            credit=4,
            level='Bachelor',
            year=1,
            semester='First',
            program=self.program
        )
        
        # Second course with a B score (70% overall)
        TakenCourse.objects.create(
            student=self.student,
            course=course2,
            assignment=70.0,
            mid_exam=70.0,
            quiz=70.0,
            attendance=70.0,
            final_exam=70.0
        )
        
        # First course: 3 credits * 4.0 (A+) = 12.0 points
        # Second course: 4 credits * 3.0 (B) = 12.0 points
        # Total points = 24.0
        # Total credits = 7
        # GPA = 24 / 7 = 3.428... ~ 3.43
        
        # The first course we created gets passed into calculation
        tc = TakenCourse.objects.first()
        gpa = tc.calculate_gpa()
        self.assertEqual(gpa, Decimal('3.43'))
