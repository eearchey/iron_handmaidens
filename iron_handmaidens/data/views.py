from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'data/home.html')

def upload(request):
    return render(request, 'data/upload.html')
