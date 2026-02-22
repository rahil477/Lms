from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages

from .decorators import lecturer_required, student_required

class LecturerLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if user.is_lecturer or user.is_superuser:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, "Bu giriş yalnız müəllimlər üçündür.")
            return self.form_invalid(form)

class StudentLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if user.is_student or user.is_superuser:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, "Bu giriş yalnız tələbələr üçündür.")
            return self.form_invalid(form)
