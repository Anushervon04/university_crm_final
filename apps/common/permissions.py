from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('login'))
            if getattr(request.user, 'role', None) not in roles:
                return redirect(reverse('login'))
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# shortcuts
def dean_required(view_func):
    return role_required('dean')(view_func)

def admin_required(view_func):
    return role_required('admin')(view_func)

def zamdekan_required(view_func):
    return role_required('zamdekan')(view_func)

def teacher_required(view_func):
    return role_required('teacher')(view_func)

def staff_required(view_func):
    return role_required('dean','admin','zamdekan','teacher')(view_func)
