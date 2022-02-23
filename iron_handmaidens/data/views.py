from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv
import io

import pandas as pd

def home(request):
    if request.method == 'POST' and request.FILES['csv-file']:
        csv_file = request.FILES['csv-file']

        df = pd.read_csv(csv_file)
        print(df)
        filename = csv_file.name
        json = df[:1].to_json()
        print(json)

        return render(request, 'data/visualize.html', {'filename': filename, 'table': df[:20].to_html(), 'json': json})
    return render(request, 'data/home.html')

def visualize(request):
    return render(request, 'data/visualize.html')

def upload(request):
    return render(request, 'upload.html')
