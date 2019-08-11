from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import File

from uploads.core.models import Document
from uploads.core.forms import DocumentForm
import ffmpeg

debug = True
fnum = 1000


def home(request):
    documents = Document.objects.all()
    return render(request, 'core/home.html', { 'documents': documents })

def pull_frame_from_video(in_filename, frame_num = 10):
    #import pdb
    #pdb.set_trace()
    out, _ = (
	    ffmpeg
	    .input(in_filename)
	    .filter('select', 'gte(n,{})'.format(frame_num))
	    .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
	    .run(capture_stdout=True)
    )
    if debug:
        print( out )
    return out


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        #uploaded_file_url = fs.url(filename)

        frame = pull_frame_from_video(str(fs.path(filename)), fnum)
        frame_file = myfile.name + "-frame-10.jpg"
        frame_name = 'media/' + frame_file
        with open(frame_name, 'w') as f:
            ffile = File(f)
            ffile.write(frame)

        #filename2 = fs.save(frame_name, frame)
        uploaded_file_url = fs.url(frame_file)

        return render(request, 'core/simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'core/simple_upload.html')


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'core/model_form_upload.html', {
        'form': form
    })
