from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def health(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('', health),
    path('health/', health),
    path('api/health/', health),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/workouts/', include('workouts.urls')),
    path('api/progress/', include('progress.urls')),
    path('api/social/', include('social.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)