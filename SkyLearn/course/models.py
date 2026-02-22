from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import ActivityLog, Semester, Notification
from core.utils import unique_slug_generator


class ProgramManager(models.Manager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query:
            or_lookup = Q(title__icontains=query) | Q(summary__icontains=query)
            queryset = queryset.filter(or_lookup).distinct()
        return queryset


class Program(models.Model):
    title = models.CharField(max_length=150, unique=True)
    summary = models.TextField(blank=True)

    objects = ProgramManager()

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("program_detail", kwargs={"pk": self.pk})


class ClassGroup(models.Model):
    title = models.CharField(max_length=100, unique=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


@receiver(post_save, sender=Program)
def log_program_save(sender, instance, created, **kwargs):
    verb = "created" if created else "updated"
    ActivityLog.objects.create(message=_(f"The program '{instance}' has been {verb}."))


@receiver(post_delete, sender=Program)
def log_program_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=_(f"The program '{instance}' has been deleted."))


class CourseManager(models.Manager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query:
            or_lookup = (
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(code__icontains=query)
                | Q(slug__icontains=query)
            )
            queryset = queryset.filter(or_lookup).distinct()
        return queryset


class Course(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=200, unique=True)
    credit = models.IntegerField(default=0)
    summary = models.TextField(max_length=200, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=settings.LEVEL_CHOICES)
    year = models.IntegerField(choices=settings.YEARS, default=1)
    semester = models.CharField(choices=settings.SEMESTER_CHOICES, max_length=200)
    is_elective = models.BooleanField(default=False)
    
    DURATION_CHOICES = (
        (6, _("6 Months")),
        (8, _("8 Months")),
        (9, _("9 Months")),
    )
    duration = models.IntegerField(choices=DURATION_CHOICES, default=6)
    
    # Grading Weights (Percentages)
    final_exam_weight = models.DecimalField(max_digits=5, decimal_places=2, default=40.0)
    mid_exam_weight = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    assignment_weight = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    quiz_weight = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    attendance_weight = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)

    objects = CourseManager()

    def __str__(self):
        return f"{self.title} ({self.code})"

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.slug})

    @property
    def is_current_semester(self):

        current_semester = Semester.objects.filter(is_current_semester=True).first()
        return self.semester == current_semester.semester if current_semester else False


@receiver(pre_save, sender=Course)
def course_pre_save_receiver(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


@receiver(post_save, sender=Course)
def log_course_save(sender, instance, created, **kwargs):
    verb = "created" if created else "updated"
    ActivityLog.objects.create(message=_(f"The course '{instance}' has been {verb}."))


@receiver(post_delete, sender=Course)
def log_course_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=_(f"The course '{instance}' has been deleted."))


class CourseAllocation(models.Model):
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="allocated_lecturer",
    )
    courses = models.ManyToManyField(Course, related_name="allocated_course")
    group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name="allocations", null=True, blank=True)
    session = models.ForeignKey(
        "core.Session", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.lecturer.get_full_name

    def get_absolute_url(self):
        return reverse("edit_allocated_course", kwargs={"pk": self.pk})


class Upload(models.Model):
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="course_files/",
        help_text=_(
            "Valid Files: pdf, docx, doc, xls, xlsx, ppt, pptx, zip, rar, 7zip"
        ),
        validators=[
            FileExtensionValidator(
                [
                    "pdf",
                    "docx",
                    "doc",
                    "xls",
                    "xlsx",
                    "ppt",
                    "pptx",
                    "zip",
                    "rar",
                    "7zip",
                ]
            )
        ],
    )
    updated_date = models.DateTimeField(auto_now=True)
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

    def get_extension_short(self):
        ext = self.file.name.split(".")[-1].lower()
        if ext in ("doc", "docx"):
            return "word"
        elif ext == "pdf":
            return "pdf"
        elif ext in ("xls", "xlsx"):
            return "excel"
        elif ext in ("ppt", "pptx"):
            return "powerpoint"
        elif ext in ("zip", "rar", "7zip"):
            return "archive"
        return "file"

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)


@receiver(post_save, sender=Upload)
def log_upload_save(sender, instance, created, **kwargs):
    if created:
        message = _(
            f"The file '{instance.title}' has been uploaded to the course '{instance.course}'."
        )
        
        # Notify all enrolled students
        from accounts.models import Student
        students = Student.objects.filter(taken_courses__course=instance.course)
        notifications = [
            Notification(
                user=student.student,
                verb=_("New material uploaded"),
                description=message,
                target_url=instance.course.get_absolute_url()
            ) for student in students
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)
            
    else:
        message = _(
            f"The file '{instance.title}' of the course '{instance.course}' has been updated."
        )
    ActivityLog.objects.create(message=message)


@receiver(post_delete, sender=Upload)
def log_upload_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        message=_(
            f"The file '{instance.title}' of the course '{instance.course}' has been deleted."
        )
    )


class UploadVideo(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.FileField(
        upload_to="course_videos/",
        help_text=_("Valid video formats: mp4, mkv, wmv, 3gp, f4v, avi, mp3"),
        validators=[
            FileExtensionValidator(["mp4", "mkv", "wmv", "3gp", "f4v", "avi", "mp3"])
        ],
    )
    summary = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse(
            "video_single", kwargs={"slug": self.course.slug, "video_slug": self.slug}
        )

    def delete(self, *args, **kwargs):
        self.video.delete(save=False)
        super().delete(*args, **kwargs)


@receiver(pre_save, sender=UploadVideo)
def video_pre_save_receiver(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


@receiver(post_save, sender=UploadVideo)
def log_uploadvideo_save(sender, instance, created, **kwargs):
    if created:
        message = _(
            f"The video '{instance.title}' has been uploaded to the course '{instance.course}'."
        )
        # Notify all enrolled students
        from accounts.models import Student
        students = Student.objects.filter(taken_courses__course=instance.course)
        notifications = [
            Notification(
                user=student.student,
                verb=_("New video uploaded"),
                description=message,
                target_url=instance.get_absolute_url()
            ) for student in students
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)
    else:
        message = _(
            f"The video '{instance.title}' of the course '{instance.course}' has been updated."
        )
    ActivityLog.objects.create(message=message)


@receiver(post_delete, sender=UploadVideo)
def log_uploadvideo_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        message=_(
            f"The video '{instance.title}' of the course '{instance.course}' has been deleted."
        )
    )


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to="assignment_files/",
        blank=True,
        null=True,
        help_text=_("Optional attachment for the assignment.")
    )
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.code}"
        
@receiver(post_save, sender=Assignment)
def log_assignment_save(sender, instance, created, **kwargs):
    verb = "created a new assignment" if created else "updated assignment"
    ActivityLog.objects.create(message=_(f"The course '{instance.course.title}' has {verb}: '{instance.title}'."))
    if created:
        from accounts.models import Student
        students = Student.objects.filter(taken_courses__course=instance.course)
        notifications = [
            Notification(
                user=s.student,
                verb=_("YENİ TAPŞIRIQ"),
                description=f"{instance.course.title} fənnindən yeni tapşırıq: {instance.title}. Son tarix: {instance.due_date.strftime('%d %M %Y, %H:%M')}",
            ) for s in students
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey("accounts.Student", on_delete=models.CASCADE, related_name="assignments_submitted")
    file = models.FileField(upload_to="assignment_submissions/")
    comments = models.TextField(blank=True, help_text=_("Optional comments by the student."))
    points_awarded = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assignment', 'student')
        
    def __str__(self):
        return f"{self.student} submission for {self.assignment.title}"

@receiver(post_save, sender=AssignmentSubmission)
def update_taken_course_assignment_score(sender, instance, **kwargs):
    if instance.points_awarded is not None:
        from result.models import TakenCourse
        from django.db.models import Avg
        taken_course = TakenCourse.objects.filter(
            student=instance.student, course=instance.assignment.course
        ).first()

        if taken_course:
            # Average points from all marked assignments in this course
            avg_point = AssignmentSubmission.objects.filter(
                student=instance.student, 
                assignment__course=instance.assignment.course,
                points_awarded__isnull=False
            ).aggregate(Avg('points_awarded'))['points_awarded__avg'] or 0
            
            taken_course.assignment = avg_point
            taken_course.save()
    """NOTE: Only department head can offer semester courses"""

    dep_head = models.ForeignKey("accounts.DepartmentHead", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.dep_head)
