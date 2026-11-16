from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(role):
    """Only lets users with the given role in. Logged-out users go to login,
    wrong-role users are sent back to their own dashboard."""

    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                messages.error(request, "You don't have access to that page.")
                return redirect('accounts:dashboard')
            return view(request, *args, **kwargs)

        return wrapper

    return decorator
