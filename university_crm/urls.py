"""
URL configuration for CRM Донишгоҳи Рақамикунонӣ 2025
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # Public pages (landing + login)
    path('', include('apps.public.urls')),
    
    # Role-based dashboards
    path('dean/', include('apps.dean.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
    path('zamdekan/', include('apps.zamdekan.urls')),
    path('teacher/', include('apps.teacher.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
