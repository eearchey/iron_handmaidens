import queue
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv
import io

from data.src.emg import EMGData

data = None

def home(request):
    # Initially shows homepage for application. After the user uploads a file, this function processes it
    # and goes to the visualize page. There is also a safety feature for if the user does not upload a file.
    global data
    # After the POST, this checks that the user has submitted a file or files into the backend.
    if request.method == 'POST' and request.FILES['csv-file']:
        files = request.FILES.getlist('csv-file')

        # Loop through all submitted files and differentiates between their formats to read them.
        for file in files:
            fileExtension = file.name.split('.')[1]
            if fileExtension == 'csv':
                newData = EMGData.read_csv(file)
            elif fileExtension == 'mat':
                newData = EMGData.read_mat(file)
            # Saving information to data
            if data == None:
                data = newData
            else:
                data += newData
        # Moves user to visualize page.
        return redirect('visualize/')
    data = None
    return render(request, 'data/home.html')

def visualize(request):
    # This page shows the user's data in a visual form, using plotly. This can be from one or multiple data files.
    global data
    # Ensuring we have data to use
    if data is None:
        return redirect('data-home')

    # Retrieving data from uploaded files if the user chooses to upload more after the first visualization.
    
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
                
        return redirect('/visualize/')

    # Preprocessing data
    table = data.quartiles().to_html()
    preprocessed = data.preprocess()
    plt = preprocessed.plot(visible=preprocessed[['RMS']], eventMarkers='Event')

    return render(request, 'data/visualize.html', {'table': table, 'plt': plt})

def upload(request):
    # This function brings the user back to the upload page? Ask Sean
    return render(request, 'data/upload.html')
