import queue
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
        files = request.FILES.getlist('csv-file')

        for file in files:
            fileExtension = file.name.split('.')[1]
            if fileExtension == 'csv':
                newData = EMGData.read_csv(file)
            elif fileExtension == 'mat':
                newData = EMGData.read_mat(file)

            if data == None:
                data = newData
            else:
                data += newData

        return redirect('visualize/')
    data = None
    return render(request, 'data/home.html')

def visualize(request):
    global data
    if data is None:
        return redirect('data-home')

    table = data.quartiles().to_html()
    preprocessed = data.preprocess()
    plt = preprocessed.plot(visible=preprocessed[['RMS']])

    return render(request, 'data/visualize.html', {'table': table, 'plt': plt})

def upload(request):
    return render(request, 'data/upload.html')
