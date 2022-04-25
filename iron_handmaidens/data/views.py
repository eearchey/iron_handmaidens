from tkinter.font import names
from django.shortcuts import render, redirect

from data.src.emg import EMGData
import glob, os
import zipfile
from django.http import FileResponse
import traceback

data, files = [], []

def home(request):
    """
    Initially shows homepage for application. After the user uploads a file, this function processes it
    and goes to the visualize page. There is also a safety feature for if the user does not upload a file.
    """
    global data

    for zip_file in glob.glob('*.zip'):
        os.remove(zip_file)
    for csv_file in glob.glob('*.csv'):
        os.remove(csv_file)

    # After the POST, this checks that the user has submitted a file or files into the backend.
    if request.method == 'POST' and ((request.FILES['MVC-file1'] and request.FILES['MG-file1']) or (request.FILES['MVC-file2'] or request.FILES['MG-file2'])):
        # Change the file and column name forms into more friendly datatypes


        files = request.FILES

        channelNames = dict(request.POST.lists())

        # Loop through all submitted files and differentiates between their formats to read them.
        for idx, filename in enumerate(files):
            if filename.startswith('MVC'):
                print(filename)
                continue
            # Names of the columns in the file being prepared for the contructor
            tags = {
                'channelNames': [channelNames['ch1Name'][idx], channelNames['ch2Name'][idx]],
                'timeName': channelNames['timestampName'][idx],
                'eventName': channelNames['eventMarker'][idx]
            }
            # Contructing the EMGData object based on the input file type


            if filename.endswith('1'):
                mvc_filename = 'MVC-file' + '1'
            else:
                mvc_filename = 'MVC-file' + '2'

            file = request.FILES[filename]
            mvc_file = request.FILES[mvc_filename]

            fileExtension = file.name.split('.')[1]
            mvc_fileExtension = mvc_file.name.split('.')[1]

            if fileExtension == 'csv':
                newData = EMGData.read_csv(file, **tags)
            elif fileExtension == 'mat':
                newData = EMGData.read_mat(file, **tags)

            if mvc_fileExtension == 'csv':
                mvc_Data = EMGData.read_csv(mvc_file, **tags)
            elif mvc_fileExtension == 'mat':
                mvc_Data = EMGData.read_mat(mvc_file, **tags)

            # Storing the EMGData
            if not data:
                print('EMG')
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
    global files
    try:
        # Ensuring we have data to use
        if not data:
            print('no data to process!')
            return redirect('data-error')
        # preprocess the data
        tables = []
        plts = []
        files = []
        for i, dataset in enumerate(data):
            print('visualize')
            tables.append(dataset.percentiles().to_html(justify='center', index=False))
            preprocessed = dataset.preprocess()
            plts.append(preprocessed.data_to_html(visible=preprocessed.find_columns(['RMS']), eventMarkers=preprocessed.eventName))
            files.append([f'data{i}.csv', preprocessed])
        return render(request, 'data/visualize.html', {'data': zip(tables, plts)})

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return redirect('data-error')


def download_zip(request):
    try:
        global files
        print(files)
        for file in files:
            file[1].data_to_csv(file[0])
        with zipfile.ZipFile('data.zip', 'w') as zipMe:
            for file in files:
                zipMe.write(file[0], compress_type=zipfile.ZIP_DEFLATED)
        return FileResponse(
            open('data.zip', 'rb'),
            as_attachment=True,
            filename='data.zip'
        )
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return redirect('data-error')


def about(request):
    return render(request, 'data/about.html')


def error(request):
    return render(request, 'data/error.html')
