from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='data-home'),
    path('upload', views.upload)
]