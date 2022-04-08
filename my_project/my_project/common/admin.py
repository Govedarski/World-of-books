from django.contrib import admin

# Register your models here.
from my_project.common.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass
