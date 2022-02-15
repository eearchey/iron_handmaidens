from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('data/', include('data.urls')),
    path('admin/', admin.site.urls),
]
