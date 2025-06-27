import os
import requests
from datetime import datetime
from django.shortcuts       import render, redirect
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth        import authenticate, login

from .models import RawDocument
from .forms  import URLForm, RegisterForm
from .utils  import extract_metadonnees, extract_full_text

def is_metadonneur(user):
    return user.groups.filter(name="Metadonneur").exists()

@login_required(login_url='rawdocs:login')
@user_passes_test(is_metadonneur, login_url='rawdocs:login')
def upload_pdf(request):
    form = URLForm(request.POST or None)
    context = {'form': form}

    if request.method == 'POST' and form.is_valid():
        url = form.cleaned_data['pdf_url']
        resp = requests.get(url)
        resp.raise_for_status()

        # Sauvegarde du PDF
        ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(url)
        rd = RawDocument(url=url, owner=request.user)
        rd.file.save(os.path.join(ts, filename), ContentFile(resp.content))
        rd.save()

        # Extraction sans IA
        metadata       = extract_metadonnees(rd.file.path, rd.url)
        extracted_text = extract_full_text(rd.file.path)

        context.update({
            'doc': rd,
            'metadata': metadata,
            'extracted_text': extracted_text,
        })

    return render(request, 'rawdocs/upload.html', context)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            uname = form.cleaned_data.get('username')
            pwd   = form.cleaned_data.get('password1')
            user  = authenticate(username=uname, password=pwd)
            login(request, user)
            return redirect('rawdocs:login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
