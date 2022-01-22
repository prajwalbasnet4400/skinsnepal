from django.http.response import JsonResponse
from django.views.generic.base import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notification

class NotificationCountView(LoginRequiredMixin,View):
    """
    View to get total number of unread notification for currently logged in User
    """ 

    def get(self,request):
        count = Notification.objects.filter(recipient=request.user,read=False).count()
        json = {'count':count}
        return JsonResponse(json)

class NotificationView(ListView):
    template_name = 'message/notification_list.html'
    model = Notification
    paginate_by = 10
    ordering = ('-date_created',)

    def get_queryset(self):
        return self.model.objects.filter(recipient=self.request.user)