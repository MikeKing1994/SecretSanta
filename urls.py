from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('creativeRutApp/', include('creativeRutApp.urls')),
    path('admin/', admin.site.urls),
]