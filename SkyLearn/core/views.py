from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import HttpResponseRedirect

from accounts.decorators import admin_required, lecturer_required
from accounts.models import User, Student
from .forms import SessionForm, SemesterForm, NewsAndEventsForm
from .models import NewsAndEvents, ActivityLog, Session, Semester, Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'core/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.target_url:
        return redirect(notification.target_url)
    return redirect('notifications')


@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')


# ########################################################
# News & Events
# ########################################################
@login_required
def home_view(request):
    items = NewsAndEvents.objects.all().order_by("-updated_date")
    context = {
        "title": "News & Events",
        "items": items,
    }
    return render(request, "core/index.html", context)


@login_required
def dashboard_view(request):
    if request.user.is_superuser:
        logs = ActivityLog.objects.all().order_by("-created_at")[:10]
        gender_count = Student.get_gender_count()
        level_count = Student.get_level_count()
        context = {
            "student_count": User.objects.get_student_count(),
            "lecturer_count": User.objects.get_lecturer_count(),
            "superuser_count": User.objects.get_superuser_count(),
            "males_count": gender_count["M"],
            "females_count": gender_count["F"],
            "bachelor_count": level_count["bachelor"],
            "master_count": level_count["master"],
            "logs": logs,
        }
        return render(request, "core/dashboard.html", context)
    
    elif request.user.is_student:
        from result.models import TakenCourse
        from course.models import Assignment, AssignmentSubmission
        from attendance.models import Attendance
        from django.db.models import Avg, Count, Q
        
        student = get_object_or_404(Student, student=request.user)
        taken_courses = TakenCourse.objects.filter(student=student)
        
        # Enrich taken_courses with attendance percentage
        for tc in taken_courses:
            attendances = Attendance.objects.filter(student=student, course=tc.course)
            total = attendances.count()
            if total > 0:
                present = attendances.filter(is_present=True).count()
                tc.attendance_percentage = (present / total) * 100
            else:
                tc.attendance_percentage = 0
                
        # Assignments pending
        # Courses the student is taking
        course_ids = taken_courses.values_list('course_id', flat=True)
        # Assignments for these courses that don't have a submission from this student
        pending_assignments = Assignment.objects.filter(course_id__in=course_ids).exclude(
            submissions__student=student
        ).order_by('due_date')
        
        context = {
            "student": student,
            "taken_courses": taken_courses,
            "pending_assignments": pending_assignments,
            "unread_notifications": Notification.objects.filter(user=request.user, is_read=False)[:5],
        }
        return render(request, "core/dashboard.html", context)

    elif request.user.is_lecturer:
        from course.models import CourseAllocation
        
        # Get ALL allocations for this lecturer to be safe
        allocations = CourseAllocation.objects.filter(lecturer=request.user).select_related('group', 'group__program')
        groups = []
        for a in allocations:
            if a.group and a.group not in groups:
                groups.append(a.group)
        
        # Identify unique specialties from these groups
        specs = []
        for g in groups:
            if g.program and g.program not in specs:
                specs.append(g.program)
        
        specialties = sorted(specs, key=lambda x: x.title)
        
        context = {
            "groups": groups,
            "specialties": specialties,
            "title": "Müəllim Paneli"
        }
        return render(request, "core/dashboard.html", context)

    return render(request, "core/dashboard.html")


@login_required
def post_add(request):
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been uploaded.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm()
    return render(request, "core/post_add.html", {"title": "Add Post", "form": form})


@login_required
@lecturer_required
def edit_post(request, pk):
    instance = get_object_or_404(NewsAndEvents, pk=pk)
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST, instance=instance)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been updated.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm(instance=instance)
    return render(request, "core/post_add.html", {"title": "Edit Post", "form": form})


@login_required
@lecturer_required
def delete_post(request, pk):
    post = get_object_or_404(NewsAndEvents, pk=pk)
    post_title = post.title
    post.delete()
    messages.success(request, f"{post_title} has been deleted.")
    return redirect("home")


# ########################################################
# Session
# ########################################################
@login_required
@lecturer_required
def session_list_view(request):
    """Show list of all sessions"""
    sessions = Session.objects.all().order_by("-is_current_session", "-session")
    return render(request, "core/session_list.html", {"sessions": sessions})


@login_required
@lecturer_required
def session_add_view(request):
    """Add a new session"""
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_session"):
                unset_current_session()
            form.save()
            messages.success(request, "Session added successfully.")
            return redirect("session_list")
    else:
        form = SessionForm()
    return render(request, "core/session_update.html", {"form": form})


@login_required
@lecturer_required
def session_update_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            if form.cleaned_data.get("is_current_session"):
                unset_current_session()
            form.save()
            messages.success(request, "Session updated successfully.")
            return redirect("session_list")
    else:
        form = SessionForm(instance=session)
    return render(request, "core/session_update.html", {"form": form})


@login_required
@lecturer_required
def session_delete_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.is_current_session:
        messages.error(request, "You cannot delete the current session.")
    else:
        session.delete()
        messages.success(request, "Session successfully deleted.")
    return redirect("session_list")


def unset_current_session():
    """Unset current session"""
    current_session = Session.objects.filter(is_current_session=True).first()
    if current_session:
        current_session.is_current_session = False
        current_session.save()


# ########################################################
# Semester
# ########################################################
@login_required
@lecturer_required
def semester_list_view(request):
    semesters = Semester.objects.all().order_by("-is_current_semester", "-semester")
    return render(request, "core/semester_list.html", {"semesters": semesters})


@login_required
@lecturer_required
def semester_add_view(request):
    if request.method == "POST":
        form = SemesterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_semester"):
                unset_current_semester()
                unset_current_session()
            form.save()
            messages.success(request, "Semester added successfully.")
            return redirect("semester_list")
    else:
        form = SemesterForm()
    return render(request, "core/semester_update.html", {"form": form})


@login_required
@lecturer_required
def semester_update_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == "POST":
        form = SemesterForm(request.POST, instance=semester)
        if form.is_valid():
            if form.cleaned_data.get("is_current_semester"):
                unset_current_semester()
                unset_current_session()
            form.save()
            messages.success(request, "Semester updated successfully!")
            return redirect("semester_list")
    else:
        form = SemesterForm(instance=semester)
    return render(request, "core/semester_update.html", {"form": form})


@login_required
@lecturer_required
def semester_delete_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if semester.is_current_semester:
        messages.error(request, "You cannot delete the current semester.")
    else:
        semester.delete()
        messages.success(request, "Semester successfully deleted.")
    return redirect("semester_list")


def unset_current_semester():
    """Unset current semester"""
    current_semester = Semester.objects.filter(is_current_semester=True).first()
    if current_semester:
        current_semester.is_current_semester = False
        current_semester.save()
@lecturer_required
def group_detail_view(request, pk):
    from course.models import ClassGroup, CourseAllocation
    group = get_object_or_404(ClassGroup, pk=pk)
    # Get courses assigned to this lecturer for THIS group
    allocations = CourseAllocation.objects.filter(lecturer=request.user, group=group)
    courses = []
    for a in allocations:
        courses.extend(list(a.courses.all()))
        
    context = {
        "group": group,
        "courses": list(set(courses)),
        "students": group.students.all().select_related('student'),
        "title": f"Qrup: {group.title}"
    }
    return render(request, "core/group_detail.html", context)


@lecturer_required
def attendance_journal_view(request, pk):
    from course.models import ClassGroup
    from datetime import date
    group = get_object_or_404(ClassGroup, pk=pk)
    # Simple mockup for current month days 1-10
    days = list(range(1, 11))
    context = {
        "group": group,
        "students": group.students.all().select_related('student'),
        "days": days,
    }
    return render(request, "core/journal.html", context)


@lecturer_required
def quiz_scoring_view(request, pk):
    from course.models import ClassGroup
    group = get_object_or_404(ClassGroup, pk=pk)
    # Get duration to determine number of months
    # We'll just assume 6 months for now as per first scenario, but can be dynamic
    months = list(range(1, 7))
    context = {
        "group": group,
        "students": group.students.all().select_related('student'),
        "months": months,
    }
    return render(request, "core/quiz_scoring.html", context)


@lecturer_required
def exam_scoring_view(request, pk):
    from course.models import ClassGroup
    group = get_object_or_404(ClassGroup, pk=pk)
    context = {
        "group": group,
        "students": group.students.all().select_related('student'),
    }
    return render(request, "core/exam_scoring.html", context)
