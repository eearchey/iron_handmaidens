from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='data-home'),
    path('visualize/', views.visualize, name='data-visualize'),
    path('upload/', views.upload, name='data-upload')
]