from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv
import io

import time

from data.preprocess import Preprocess

def home(request):
    if request.method == 'POST' and request.FILES['csv-file']:
        start = time.time()
        csv_file = request.FILES['csv-file']

        data = Preprocess.read_csv(csv_file)
        data.run()

        filename = csv_file.name
        table = data.quartiles().to_html()
        plt = data.plot(visible=data.find_columns('Moving'))

        end = time.time()
        print(f'Spent {end-start} seconds in the backend')
        return render(request, 'data/visualize.html', {'filename': filename, 'table': table, 'plt': plt})

    return render(request, 'data/home.html')

def visualize(request):
    return render(request, 'data/visualize.html')

def upload(request):
    return render(request, 'upload.html')
