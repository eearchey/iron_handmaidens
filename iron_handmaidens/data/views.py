from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv
import io

def home(request):
    if request.method == 'POST' and request.FILES['csv-file']:
        csv_file = request.FILES['csv-file']
        filename = csv_file.name
        # Read csv file InMemoryUploadedFile
        file = csv_file.read().decode('utf-8-sig')
        return render(request, 'data/visualize.html', {'filename': filename})
    return render(request, 'data/home.html')

def visualize(request):
    return render(request, 'data/visualize.html')
