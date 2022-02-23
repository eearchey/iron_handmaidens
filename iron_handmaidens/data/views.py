from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv
import io

import pandas as pd
from plotly.offline import plot
import plotly.express as px

def home(request):
    if request.method == 'POST' and request.FILES['csv-file']:
        csv_file = request.FILES['csv-file']

        df = pd.read_csv(csv_file)
        filename = csv_file.name

        fig = px.line(df[:1000], 'Timestamp_4680', ['CH1_4680', 'CH2_4680'])
        plt = plot(fig, output_type='div')

        return render(request, 'data/visualize.html', {'filename': filename, 'table': df[:20].to_html(), 'plt': plt})
    return render(request, 'data/home.html')

def visualize(request):
    return render(request, 'data/visualize.html')

def upload(request):
    return render(request, 'upload.html')
