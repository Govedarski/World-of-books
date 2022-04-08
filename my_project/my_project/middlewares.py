import logging

from django.core.checks import Debug
from django.shortcuts import render


def handle_server_internal_error(get_response):
    def middleware(request):
        result = get_response(request)
        if result.status_code >= 500 and not Debug:
            logging.error(f"Error catch by middleware in {request.path}")
            return render(request, '500.html')
        return result

    return middleware
