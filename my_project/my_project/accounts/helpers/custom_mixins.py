from django.shortcuts import redirect


class LogoutRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('show_home')
        return super().dispatch(request, *args, **kwargs)

