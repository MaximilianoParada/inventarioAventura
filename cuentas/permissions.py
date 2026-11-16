from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Role, UserRole


def get_role_names(user):
    if not user.is_authenticated:
        return []

    role_names = list(
        UserRole.objects.filter(user_id=user).values_list('role__role_name', flat=True)
    )
    if user.is_superuser and Role.ADMINISTRATOR not in role_names:
        role_names.append(Role.ADMINISTRATOR)
    return role_names


def has_role(user, role_name):
    if not user.is_authenticated:
        return False
    if role_name == Role.ADMINISTRATOR and user.is_superuser:
        return True
    return UserRole.objects.filter(user_id=user, role__role_name=role_name).exists()


def is_administrator(user):
    return has_role(user, Role.ADMINISTRATOR)


def is_guide_operator(user):
    return is_administrator(user) or has_role(user, Role.GUIDE_OPERATOR)


def is_tourist_client(user):
    return has_role(user, Role.TOURIST_CLIENT)


def dashboard_permissions(user):
    permissions = {
        'administrador': 0,
        'guia': 0,
        'operador': 0,
        'turista': 0,
        'cliente': 0,
    }

    assignments = UserRole.objects.filter(user_id=user).select_related('role')
    for assignment in assignments:
        for permission in permissions:
            permissions[permission] = max(
                permissions[permission],
                getattr(assignment.role, permission),
            )

    if user.is_superuser:
        permissions['administrador'] = 2

    return permissions


def role_required(*role_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not any(has_role(request.user, role_name) for role_name in role_names):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
