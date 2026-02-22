from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import TakenCourse
from core.models import Notification
from course.models import AssignmentSubmission

@receiver(post_save, sender=TakenCourse)
def notify_grade_update(sender, instance, created, **kwargs):
    # Only notify if total > 0 (meaning a score was entered or remains significant)
    if instance.total > 0:
        # Check if the save was triggered by a grade change
        # (In a real scenario, we might want to check dirty fields, 
        # but here we follow the user logic: notify on entry or update)
        
        verb = _("daxil edildi") if created else _("yenisindən qiymətləndirildi")
        title = _("Qiymət Bildirişi")
        message = _(f"{instance.course.title} fənnindən qiymətiniz {verb}: {instance.total} ({instance.grade})")
        
        # 1. In-app notification
        Notification.objects.create(
            user=instance.student.student,
            verb=title,
            description=message
        )
        
        # 2. Email notification
        subject = f"{title}: {instance.course.title}"
        html_message = render_to_string('accounts/email/grade_notification.html', {
            'student': instance.student,
            'course': instance.course,
            'total': instance.total,
            'grade': instance.grade,
            'verb': verb
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.student.student.email],
            html_message=html_message,
            fail_silently=True
        )

@receiver(post_save, sender=AssignmentSubmission)
def notify_assignment_grade_update(sender, instance, **kwargs):
    # Only notify if points_awarded is set (marked)
    if instance.points_awarded is not None:
        title = _("Tapşırıq Qiymətləndirildi")
        message = _(f"{instance.assignment.course.title} fənnindən '{instance.assignment.title}' tapşırığı qiymətləndirildi: {instance.points_awarded}")
        
        # 1. In-app notification
        Notification.objects.create(
            user=instance.student.student,
            verb=title,
            description=message
        )
        
        # 2. Email notification
        subject = f"{title}: {instance.assignment.title}"
        html_message = render_to_string('accounts/email/grade_notification.html', {
            'student': instance.student,
            'course': instance.assignment.course,
            'total': instance.points_awarded,
            'grade': "-", # Assignment doesn't have a letter grade usually
            'verb': _("qiymətləndirildi")
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.student.student.email],
            html_message=html_message,
            fail_silently=True
        )
