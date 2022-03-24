from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views import generic as views


class ShowHomePageView(views.TemplateView):
    template_name = 'home_page.html'
