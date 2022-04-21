from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='data-home'),
    path('visualize/', views.visualize, name='data-visualize'),
    path('about/', views.about, name='data-about'),
    path('error/', views.error, name='data-error'),
    path('visualize/download_zip/', views.download_zip, name="data-download_zip")
]