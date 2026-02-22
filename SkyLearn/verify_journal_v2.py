import os
import django
import sys

# Setup Django environment
sys.path.append(r'd:\R\Code\SkyLearn\SkyLearn')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from attendance.models import Attendance
from course.models import Course
from accounts.models import Student
from django.utils import timezone

def verify_journal_v2():
    print("Starting Excel-based Journal verification...")
    
    # Get a test course and student
    course = Course.objects.first()
    student = Student.objects.first()
    test_date = timezone.now().date()
    
    if not course or not student:
        print("Error: No course or student found in database.")
        return

    print(f"Testing for Course: {course.title}, Student: {student.student.get_full_name}, Date: {test_date}")

    # Test saving with note
    test_note = "Tələbə fəal iştirak edir."
    attendance, created = Attendance.objects.update_or_create(
        course=course,
        student=student,
        date=test_date,
        defaults={'is_present': True, 'point': 9, 'note': test_note, 'is_locked': False}
    )
    print(f"Record created/updated: Point={attendance.point}, Note='{attendance.note}', Locked={attendance.is_locked}")
    assert attendance.point == 9
    assert attendance.note == test_note
    assert not attendance.is_locked

    print("Verification script (v2) completed successfully.")

if __name__ == "__main__":
    verify_journal_v2()
