from decimal import Decimal
from django.conf import settings

from django.db import models
from django.urls import reverse

from accounts.models import Student
from core.models import Semester
from course.models import Course

A_PLUS = "A+"
A = "A"
A_MINUS = "A-"
B_PLUS = "B+"
B = "B"
B_MINUS = "B-"
C_PLUS = "C+"
C = "C"
C_MINUS = "C-"
D = "D"
F = "F"
NG = "NG"

GRADE_CHOICES = (
    (A_PLUS, "A+"),
    (A, "A"),
    (A_MINUS, "A-"),
    (B_PLUS, "B+"),
    (B, "B"),
    (B_MINUS, "B-"),
    (C_PLUS, "C+"),
    (C, "C"),
    (C_MINUS, "C-"),
    (D, "D"),
    (F, "F"),
    (NG, "NG"),
)

PASS = "PASS"
FAIL = "FAIL"

COMMENT_CHOICES = (
    (PASS, "PASS"),
    (FAIL, "FAIL"),
)

GRADE_BOUNDARIES = [
    (90, A_PLUS),
    (85, A),
    (80, A_MINUS),
    (75, B_PLUS),
    (70, B),
    (65, B_MINUS),
    (60, C_PLUS),
    (55, C),
    (50, C_MINUS),
    (45, D),
    (0, F),
]

GRADE_POINT_MAPPING = {
    A_PLUS: 4.0,
    A: 4.0,
    A_MINUS: 3.75,
    B_PLUS: 3.5,
    B: 3.0,
    B_MINUS: 2.75,
    C_PLUS: 2.5,
    C: 2.0,
    C_MINUS: 1.75,
    D: 1.0,
    F: 0.0,
    NG: 0.0,
}


class MonthlyQuizScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="monthly_quiz_scores")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    month_number = models.IntegerField(help_text="1 to 9")
    score = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"), help_text="Max score per month depends on duration (3, 4, or 5)")
    is_locked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "course", "month_number")

    def __str__(self):
        return f"{self.student} - {self.course} - Month {self.month_number}: {self.score}"


class TakenCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="taken_courses"
    )
    assignment = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    mid_exam = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    quiz = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    attendance = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    final_exam = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    total = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), editable=False
    )
    grade = models.CharField(
        choices=GRADE_CHOICES, max_length=2, blank=True, editable=False
    )
    point = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), editable=False
    )
    comment = models.CharField(
        choices=COMMENT_CHOICES, max_length=200, blank=True, editable=False
    )
    # Locking for Teacher (Admin can override)
    is_final_exam_locked = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.course.slug})

    def __str__(self):
        return f"{self.course.title} ({self.course.code})"

    def get_total(self):
        # 50/50 Split logic based on course duration
        duration = self.course.duration
        
        # 1. Final Exam (50 points)
        final_score = Decimal(self.final_exam)
        
        # 2. Activity/Attendance
        # Daily activity logic: users mentioned specific values for different durations
        # 6 mo: 20 pts, 8 mo: 18 pts, 9 mo: 23 pts
        activity_weight = Decimal("20.00")
        if duration == 8:
            activity_weight = Decimal("18.00")
        elif duration == 9:
            activity_weight = Decimal("23.00")
        
        # Current logic uses self.attendance as a 0-100 scale usually
        # We'll treat self.attendance as the percentage of activity/attendance points earned
        earned_activity = (Decimal(self.attendance) * activity_weight) / Decimal("100.00")
        
        # 3. Monthly Quizzes
        # 6 mo: 30 pts (6x5), 8 mo: 32 pts (8x4), 9 mo: 27 pts (9x3)
        monthly_scores = MonthlyQuizScore.objects.filter(student=self.student, course=self.course)
        earned_quiz = sum([s.score for s in monthly_scores])
        
        # self.quiz field will be synced from the sum of monthly scores for backwards compatibility/display
        return final_score + earned_activity + earned_quiz

    def get_grade(self):
        total = self.total
        for boundary, grade in GRADE_BOUNDARIES:
            if total >= boundary:
                return grade
        return NG

    def get_comment(self):
        if self.grade in [F, NG]:
            return FAIL
        return PASS

    def get_point(self):
        credit = self.course.credit
        grade_point = GRADE_POINT_MAPPING.get(self.grade, 0.0)
        return Decimal(credit) * Decimal(grade_point)

    def save(self, *args, **kwargs):
        self.total = self.get_total()
        self.grade = self.get_grade()
        self.point = self.get_point()
        self.comment = self.get_comment()
        super().save(*args, **kwargs)

    def calculate_gpa(self):
        current_semester = Semester.objects.filter(is_current_semester=True).first()
        if not current_semester:
            return Decimal("0.00")

        taken_courses = TakenCourse.objects.filter(
            student=self.student,
            course__level=self.student.level,
            course__semester=current_semester.semester,
        )

        total_points = sum(tc.point for tc in taken_courses)
        total_credits = sum(tc.course.credit for tc in taken_courses)

        if total_credits > 0:
            gpa = total_points / Decimal(total_credits)
            return round(gpa, 2)
        return Decimal("0.00")

    def calculate_cgpa(self):
        taken_courses = TakenCourse.objects.filter(student=self.student)

        total_points = sum(tc.point for tc in taken_courses)
        total_credits = sum(tc.course.credit for tc in taken_courses)

        if total_credits > 0:
            cgpa = total_points / Decimal(total_credits)
            return round(cgpa, 2)
        return Decimal("0.00")


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    gpa = models.FloatField(null=True)
    cgpa = models.FloatField(null=True)
    semester = models.CharField(max_length=100, choices=settings.SEMESTER_CHOICES)
    session = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=25, choices=settings.LEVEL_CHOICES, null=True)

    def __str__(self):
        return f"Result for {self.student} - Semester: {self.semester}, Level: {self.level}"
