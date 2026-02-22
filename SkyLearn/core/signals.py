from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Notification
from course.models import Upload, UploadVideo
from quiz.models import Quiz
from result.models import TakenCourse

@receiver(post_save, sender=Upload)
def notify_new_upload(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        students = TakenCourse.objects.filter(course=course).values_list('student__student', flat=True)
        for student_id in students:
            Notification.objects.create(
                user_id=student_id,
                verb=f"Yeni sənəd əlavə edildi: {instance.title}",
                description=f"'{course.title}' kursuna yeni sənəd əlavə edildi.",
                target_url=course.get_absolute_url()
            )

@receiver(post_save, sender=UploadVideo)
def notify_new_video(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        students = TakenCourse.objects.filter(course=course).values_list('student__student', flat=True)
        for student_id in students:
            Notification.objects.create(
                user_id=student_id,
                verb=f"Yeni video dərs əlavə edildi: {instance.title}",
                description=f"'{course.title}' kursuna yeni video dərs əlavə edildi.",
                target_url=instance.get_absolute_url()
            )

@receiver(post_save, sender=Quiz)
def notify_new_quiz(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        students = TakenCourse.objects.filter(course=course).values_list('student__student', flat=True)
        for student_id in students:
            Notification.objects.create(
                user_id=student_id,
                verb=f"Yeni test imtahanı əlavə edildi: {instance.title}",
                description=f"'{course.title}' kursuna yeni test imtahanı əlavə edildi.",
                target_url=instance.get_absolute_url()
            )
