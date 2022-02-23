from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv
import io
from data.preprocess import Preprocess

def home(request):
    if request.method == 'POST' and request.FILES['csv-file']:
        csv_file = request.FILES['csv-file']

        data = Preprocess.read_csv(csv_file)

        filename = csv_file.name
        table = data.df[:20].to_html()
        plt = data.plot(cap=100000)

        return render(request, 'data/visualize.html', {'filename': filename, 'table': table, 'plt': plt})
    return render(request, 'data/home.html')

def visualize(request):
    return render(request, 'data/visualize.html')

def upload(request):
    return render(request, 'upload.html')
