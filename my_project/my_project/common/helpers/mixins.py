from django.contrib.auth.mixins import LoginRequiredMixin


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
        if len(self.object_list) > self.paginate_by:
            context['see_more'] = True
        return context