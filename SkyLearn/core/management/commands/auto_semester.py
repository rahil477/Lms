from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Semester, Session, ActivityLog

class Command(BaseCommand):
    help = 'Automatically transitions to the next semester if the current one has ended.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        current_semester = Semester.objects.filter(is_current_semester=True).first()

        if not current_semester:
            self.stdout.write(self.style.WARNING("No current semester found."))
            return

        if current_semester.next_semester_begins and today >= current_semester.next_semester_begins:
            self.stdout.write(f"Transitioning from {current_semester.semester} semester...")
            
            # Logic to find the next semester
            next_sem_name = None
            next_session = current_semester.session
            
            if current_semester.semester == 'First':
                next_sem_name = 'Second'
            elif current_semester.semester == 'Second':
                next_sem_name = 'Third'
            else: # Third or Last
                next_sem_name = 'First'
                # Find or create next session
                current_session_val = current_semester.session.session
                try:
                    # Expecting format like 2023/2024
                    start_year, end_year = map(int, current_session_val.split('/'))
                    next_session_val = f"{start_year + 1}/{end_year + 1}"
                    next_session, _ = Session.objects.get_or_create(session=next_session_val)
                    # Sync session flags
                    Session.objects.all().update(is_current_session=False)
                    next_session.is_current_session = True
                    next_session.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Could not determine next session: {e}"))
                    return

            # Find the new semester object
            new_semester, created = Semester.objects.get_or_create(
                semester=next_sem_name,
                session=next_session
            )

            # Perform the switch
            Semester.objects.all().update(is_current_semester=False)
            new_semester.is_current_semester = True
            new_semester.save()

            msg = f"Automatically transitioned to {new_semester.semester} semester of {next_session.session} session."
            ActivityLog.objects.create(message=msg)
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stdout.write("No transition needed today.")
