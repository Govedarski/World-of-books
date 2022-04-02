from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render
from django.views import generic as views
from django.views.generic import ListView, DetailView

from my_project.common.models import Notification


class ShowHomePageView(views.TemplateView):
    template_name = 'home_page.html'


class ShowNotificationsView(ListView):
    template_name = 'common/notifications/show_notifications.html'
    context_object_name = 'notifications'
    model = Notification
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_notifications'] = True
        if len(self.object_list) > self.paginate_by:
            context['see_more'] = True
        return context

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class DetailsNotificationView(DetailView):
    model = Notification
    context_object_name = 'notification'
    template_name = 'common/notifications/notifications_details.html'

    def dispatch(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        if notification.offer:
            return redirect('show_offer_details', pk=notification.offer.pk)
        return super().dispatch(request, *args, **kwargs)
