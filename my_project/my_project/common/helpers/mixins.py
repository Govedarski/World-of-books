from abc import abstractmethod

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class CustomLoginRequiredMixin(LoginRequiredMixin):
    is_login_required = True


class RemoveHelpTextMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None


class AddCCSMixin:
    def _add_ccs(self, *args):
        for field in self.fields.values():
            for klass in args:
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = ''
                field.widget.attrs['class'] += ' ' + klass


class PaginationShowMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_set = self.get_queryset()
        if len(query_set) > self.paginate_by:
            context['see_more'] = True
        return context


class AuthorizationRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        authorized_users = [getattr(obj, field) for field in self.authorizing_fields]
        return self.request.user in authorized_users

