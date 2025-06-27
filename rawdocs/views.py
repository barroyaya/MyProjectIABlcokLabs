import os
import requests
import json
from datetime import datetime

from django.shortcuts       import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.http            import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth    import authenticate, login

from .models import RawDocument
from .forms  import URLForm, RegisterForm
from .utils  import extract_metadonnees, extract_full_text

from django.shortcuts import render
from .models import RawDocument


def dashboard_view(request):
    documents = RawDocument.objects.all()

    total_scrapped = documents.count()
    total_planned = 150

    # On ne filtre plus par "status" car ce champ n'existe pas
    total_completed = 0   # ou à calculer autrement
    total_rejected = 0    # idem
    total_in_reextraction = 25
    in_progress = 12
    rescrapping = 3

    context = {
        'total_scrapped': total_scrapped,
        'total_planned': total_planned,
        'total_completed': total_completed,
        'in_progress': in_progress,
        'tasks_extraction': 15,
        'tasks_validation': 8,
        'tasks_annotation': 12,
        'tasks_correction': 5,
        'tasks_finalisation': 3,
        # pré-encode les données pour JavaScript
        'bar_data': json.dumps([total_planned, total_scrapped, total_completed, in_progress]),
        'pie_data': json.dumps([15, 8, 12, 5, 3]),
    }
    return render(request, 'rawdocs/dashboard.html', context)



def is_metadonneur(user):
    return user.groups.filter(name="Metadonneur").exists()


@login_required(login_url='rawdocs:login')
@user_passes_test(is_metadonneur, login_url='rawdocs:login')
def upload_pdf(request):
    form    = URLForm(request.POST or None)
    context = {'form': form}

    if request.method == 'POST' and form.is_valid():
        url  = form.cleaned_data['pdf_url']
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


@login_required(login_url='rawdocs:login')
@user_passes_test(is_metadonneur, login_url='rawdocs:login')
def document_list(request):
    """
    Affiche tous les RawDocument importés par l'utilisateur connecté.
    """
    documents = RawDocument.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'rawdocs/document_list.html', {
        'documents': documents
    })


@login_required(login_url='rawdocs:login')
@user_passes_test(is_metadonneur, login_url='rawdocs:login')
def document_metadata(request, doc_id):
    """
    Renvoie en JSON les métadonnées extraites pour le RawDocument d'id=doc_id.
    """
    rd = get_object_or_404(RawDocument, id=doc_id, owner=request.user)
    metadata = extract_metadonnees(rd.file.path, rd.url)
    return JsonResponse(metadata)


@login_required(login_url='rawdocs:login')
@user_passes_test(is_metadonneur, login_url='rawdocs:login')
def delete_document(request, doc_id):
    """
    Supprime définitivement le RawDocument d'id=doc_id.
    """
    rd = get_object_or_404(RawDocument, id=doc_id, owner=request.user)
    if request.method == 'POST':
        rd.delete()
        return redirect('rawdocs:document_list')
    # En cas de GET on redirige simplement vers la liste
    return redirect('rawdocs:document_list')
