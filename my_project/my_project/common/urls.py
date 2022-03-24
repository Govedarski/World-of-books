from django.contrib import admin
from django.urls import path

from my_project.common.views import ShowHomePageView

urlpatterns = [
    path('', ShowHomePageView.as_view(), name = 'show_home'),
]
