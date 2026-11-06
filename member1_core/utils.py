from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Target

SCAN_ROLES = {"admin", "analyst"}


def get_role(user):
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", "") if profile else ""


def can_scan(user):
    return user.is_superuser or get_role(user) in SCAN_ROLES


def visible_targets(user):
    qs = Target.objects.all()
    if user.is_superuser or get_role(user) in SCAN_ROLES:
        return qs
    return qs.filter(owner=user)


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.user.is_superuser or get_role(request.user) in roles:
                return view(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission.")
        return wrapper
    return decorator