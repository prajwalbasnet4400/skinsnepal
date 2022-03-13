from django.http import JsonResponse
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'chat/index.html'