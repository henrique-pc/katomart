from django.urls import path
from django.http import HttpResponse

def placeholder_view(request):
    return HttpResponse('Backups app placeholder')

urlpatterns = [
    path('', placeholder_view, name='backups-placeholder'),
] 