from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv
import io

from data.src.emg import EMGData

data = None

def home(request):
    global data
    if request.method == 'POST' and request.FILES['csv-file']:
        csv_file = request.FILES['csv-file']

        if data is None:
            data = EMGData.read_csv(csv_file).preprocess()
        else:
            data = data + EMGData.read_csv(csv_file).preprocess()

        return redirect('visualize/')

    return render(request, 'data/home.html')

def visualize(request):
    global data
    if data is None:
        return redirect('data-home')

    table = data.quartiles().to_html()
    plt = data.plot(visible=data.find_columns('Moving'))

    return render(request, 'data/visualize.html', {'table': table, 'plt': plt})

def upload(request):
    return render(request, 'upload.html')
