from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import ProfileForm, RegisterForm
from .models import User


def home(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return redirect('accounts:login')


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('accounts:login')
        messages.error(request, 'Please fix the errors below.')
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    """Sends each user to the dashboard for their role."""
    if request.user.role == User.Role.ADMIN:
        return redirect('accounts:admin_dashboard')
    return redirect('accounts:student_dashboard')


@role_required(User.Role.STUDENT)
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role=User.Role.STUDENT).count(),
        'total_admins': User.objects.filter(role=User.Role.ADMIN).count(),
        'recent_users': User.objects.order_by('-date_joined')[:10],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def profile(request):
    # always the logged-in user, there is no id in the URL
    return render(request, 'accounts/profile.html', {'profile_user': request.user})


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
        messages.error(request, 'Please fix the errors below.')
    return render(request, 'accounts/profile_edit.html', {'form': form})
