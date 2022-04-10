from django.core.exceptions import PermissionDenied


def staff_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        raise PermissionDenied

    return wrapper
