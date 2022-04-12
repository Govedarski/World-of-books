from allauth.account.adapter import DefaultAccountAdapter

# Create your views here.
from django.urls import reverse_lazy


class MyAccountAdapter(DefaultAccountAdapter):
    ''' Allauth login redirect to next'''
    def get_login_redirect_url(self, request):
        next_page = self.request.GET.get('next')
        return next_page if next_page else reverse_lazy('show_home')