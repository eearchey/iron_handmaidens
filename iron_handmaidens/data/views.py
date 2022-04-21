from tkinter.font import names
from django.shortcuts import render, redirect

from data.src.emg import EMGData

data = []

def home(request):
    """
    Initially shows homepage for application. After the user uploads a file, this function processes it
    and goes to the visualize page. There is also a safety feature for if the user does not upload a file.
    """
    global data

    # After the POST, this checks that the user has submitted a file or files into the backend.
    if request.method == 'POST' and request.FILES['csv-file']:
        # Change the file and column name forms into more friendly datatypes
        files = request.FILES.getlist('csv-file')
        channelNames = dict(request.POST.lists())

        # Loop through all submitted files and differentiates between their formats to read them.
        for idx, file in enumerate(files):
            # Names of the columns in the file being prepared for the contructor
            tags = {
                'channelNames': [channelNames['ch1Name'][idx], channelNames['ch2Name'][idx]],
                'timeName': channelNames['timestampName'][idx],
                'eventName': channelNames['eventMarker'][idx]
            }
            # Contructing the EMGData object based on the input file type
            fileExtension = file.name.split('.')[1]
            if fileExtension == 'csv':
                newData = EMGData.read_csv(file, **tags)
            elif fileExtension == 'mat':
                newData = EMGData.read_mat(file, **tags)

            # Storing the EMGData
            if not data:
                data.append(newData)
            else:
                try:
                    data[0] = data[0].merge(newData)
                except ValueError as e:
                    print('Skipping file: ' + file.name)
                    print('Reason:', e)

        # Redirecting to the visualize the data
        return redirect('visualize/')
    data = []
    return render(request, 'data/home.html')

def visualize(request):
    """
    This page shows the user's data in a visual form, using plotly. This can be from one or multiple data files.
    """
    global data
    try:
        # Ensuring we have data to use
        if not data:
            return redirect('data-error')
        # Retrieving data from uploaded files if the user chooses to upload more after the first visualization.
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
                    data[0] = data[0].merge(newData)

            return redirect('/visualize/')
        # preprocess the data
        tables = []
        plts = []
        for dataset in data:
            tables.append(dataset.percentiles().to_html(justify='center', index=False))
            preprocessed = dataset.preprocess()
            plts.append(preprocessed.data_to_html(visible=preprocessed.find_columns(['RMS']), eventMarkers=preprocessed.eventName))

        return render(request, 'data/visualize.html', {'data': zip(tables, plts)})

    except Exception as e:
        print(e)
        return redirect('data-error')

def about(request):
    return render(request, 'data/about.html')


def error(request):
    return render(request, 'data/error.html')
