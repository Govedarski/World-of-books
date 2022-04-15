from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def staff_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        raise PermissionDenied

    return wrapper


def access_required(Model, *access_grant_fields):
    def decorator(function):
        def wrapper(request, pk):
            my_obj = get_object_or_404(Model, pk=pk)
            has_access = any(request.user == getattr(my_obj, field) for field in access_grant_fields)
            if not has_access:
                raise PermissionDenied()
            result = function(request, pk, my_obj)
            return result

        return wrapper

    return decorator
