from django.shortcuts import render, redirect

from data.src.emg import EMGData

data = []

def home(request):
    global data
    if request.method == 'POST' and request.FILES['csv-file']:
        files = request.FILES.getlist('csv-file')
        print(request.POST)
        tags = {'channels': ['CH1_4680', 'CH2_4680'], 'time': 'Timestamp_4680', 'event': 'Event_4680'}
        for file in files:
            fileExtension = file.name.split('.')[1]
            if fileExtension == 'csv':
                newData = EMGData.read_csv(file, **tags)
            elif fileExtension == 'mat':
                newData = EMGData.read_mat(file, **tags)

            if not data:
                data.append(newData)
            else:
                data[0] += newData

        return redirect('visualize/')
    data = []
    return render(request, 'data/home.html')

def visualize(request):
    global data
    if not data:
        return redirect('data-home')

    if request.method == 'POST' and request.FILES['csv-file']:
        files = request.FILES.getlist('csv-file')
        tags = {'channels': ['CH1_4680', 'CH2_4680'], 'time': 'Timestamp_4680', 'event': 'Event_4680'}
        for file in files:
            fileExtension = file.name.split('.')[1]
            if fileExtension == 'csv':
                newData = EMGData.read_csv(file, **tags)
            elif fileExtension == 'mat':
                newData = EMGData.read_mat(file, **tags)

            if not data:
                data.append(newData)
            else:
                data[0] += newData

        return redirect('/visualize/')

    tables = []
    plts = []
    for dataset in data:
        tables.append(dataset.quartiles().to_html())
        preprocessed = dataset.preprocess()
        plts.append(preprocessed.plot(visible=preprocessed[['RMS']], eventMarkers='Event'))

    return render(request, 'data/visualize.html', {'data': zip(tables, plts)})

def upload(request):
    return render(request, 'data/upload.html')
