from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect
# Create your views here.
from django.views import generic as views
from django.views.generic import ListView, DetailView

from my_project.common.helpers.custom_mixins import AuthorizationRequiredMixin
from my_project.common.models import Notification
from my_project.library.models import Book


class ShowHomePageView(views.TemplateView):
    template_name = 'home_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.prefetch_related('likes'). \
                    filter(owner__isnull=False). \
                    annotate(like_count=Count('likes')). \
                    order_by('-like_count', 'title'). \
                    all()[:3]
        context['books_to_show'] = books
        return context


class ShowNotificationsView(LoginRequiredMixin, ListView):
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


class DetailsNotificationView(LoginRequiredMixin, AuthorizationRequiredMixin, DetailView):
    model = Notification
    context_object_name = 'notification'
    template_name = 'common/notifications/notifications_details.html'
    authorizing_fields = ['recipient']

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        if notification.offer:
            return redirect('show_offer_details', pk=notification.offer.pk)
        return result
