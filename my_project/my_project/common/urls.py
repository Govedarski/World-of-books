from django.contrib import admin
from django.urls import path

from my_project.common.views import ShowHomePageView, ShowNotificationsView, DetailsNotificationView

urlpatterns = [
    path('', ShowHomePageView.as_view(), name='show_home'),
    path('notifications/', ShowNotificationsView.as_view(), name='show_notifications'),
    path('notification/details/<int:pk>/', DetailsNotificationView.as_view(), name='notification_details'),
]
