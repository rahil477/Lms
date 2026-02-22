from accounts.models import User
from course.models import ClassGroup, Course, CourseAllocation, Program
from core.models import Session

# 1. Target existing program and course
# Based on subagent, Program ID 1 is Qrafik Dizayn, course is QR1010
pg = Program.objects.get(id=1) 
subj = Course.objects.filter(program=pg).first() # Grab the first course in that program

# 2. Re-link test.teacher
u = User.objects.get(username='test.teacher')
u.is_lecturer = True
u.is_active = True
u.save()

# 3. Create/Link Group for this program
grp, _ = ClassGroup.objects.get_or_create(title='305D', program=pg)

# 4. Session
sess = Session.objects.filter(is_current_session=True).first() or Session.objects.first()

# 5. Clear old allocations for this user to be clean
CourseAllocation.objects.filter(lecturer=u).delete()

# 6. New Allocation
ca = CourseAllocation.objects.create(lecturer=u, group=grp, session=sess)
ca.courses.add(subj)

print(f"SUCCESS: test.teacher linked to {pg.title} - {subj.title} ({subj.code}) - Group {grp.title}")
