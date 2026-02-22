from accounts.models import User
from course.models import ClassGroup, Course, CourseAllocation
from core.models import Session, Semester

print("--- USERS ---")
for u in User.objects.filter(is_lecturer=True):
    print(f"Lecturer: {u.username}")

print("\n--- GROUPS ---")
for g in ClassGroup.objects.all():
    print(f"Group: {g.title} (ID: {g.id}) - Program: {g.program}")

print("\n--- COURSES ---")
for c in Course.objects.all():
    print(f"Course: {c.title} (Code: {c.code}) - ID: {c.id}")

print("\n--- ALLOCATIONS ---")
for a in CourseAllocation.objects.all():
    print(f"Allocation: Lecturer={a.lecturer.username}, Group={a.group.title if a.group else 'NONE'}, Session={a.session}")

print("\n--- SESSIONS/SEMESTERS ---")
for s in Session.objects.all():
    print(f"Session: {s.session} - Current: {s.is_current_session}")
for sem in Semester.objects.all():
    print(f"Semester: {sem.semester} - Current: {sem.is_current_semester} - Session: {sem.session}")
