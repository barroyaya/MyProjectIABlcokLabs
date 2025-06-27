import os
import requests
import json
from datetime import datetime

from django.shortcuts       import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.http            import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth    import authenticate, login

from .models import RawDocument, MetadataLog
from .forms  import URLForm, RegisterForm, MetadataEditForm
from .utils  import extract_metadonnees, extract_full_text


def is_metadonneur(user):
    return user.groups.filter(name="Metadonneur").exists()


@login_required(login_url='rawdocs:login')
@user_passes_test(is_metadonneur, login_url='rawdocs:login')
def dashboard_view(request):
    documents = RawDocument.objects.filter(owner=request.user)
    total_scrapped        = documents.count()
    total_planned         = 150
    total_completed       = 0    # adapter si vous stockez un statut
    total_rejected        = 0
    total_in_reextraction = 25
    in_progress           = 12
    rescrapping           = 3

    context = {
        'total_scrapped':     total_scrapped,
        'total_planned':      total_planned,
        'total_completed':    total_completed,
        'in_progress':        in_progress,
        'tasks_extraction':   15,
        'tasks_validation':   8,
        'tasks_annotation':   12,
        'tasks_correction':   5,
        'tasks_finalisation': 3,
        'bar_data':  json.dumps([total_planned, total_scrapped, total_completed, in_progress]),
        'pie_data':  json.dumps([15, 8, 12, 5, 3]),
    }
    return render(request, 'rawdocs/dashboard.html', context)


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

        # Exposer un attribut basename pour le template
        rd.basename = os.path.basename(rd.file.name)

        # Extraction sans IA
        metadata       = extract_metadonnees(rd.file.path, rd.url)
        extracted_text = extract_full_text(rd.file.path)

        context.update({
            'doc':            rd,
            'metadata':       metadata,
            'extracted_text': extracted_text,
        })

    return render(request, 'rawdocs/upload.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            uname = form.cleaned_data['username']
            pwd   = form.cleaned_data['password1']
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
    # Prépare basename pour chaque document
    for doc in documents:
        doc.basename = os.path.basename(doc.file.name)

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


@login_required(login_url='rawdocs:login')
@user_passes_test(is_metadonneur, login_url='rawdocs:login')
def edit_metadata(request, doc_id):
    """
    Affiche/traite le formulaire d'édition des métadonnées et journalise les modifications.
    """
    rd = get_object_or_404(RawDocument, id=doc_id, owner=request.user)
    # Exposer basename pour le template
    rd.basename = os.path.basename(rd.file.name)

    # On extrait à la volée pour afficher les valeurs courantes
    metadata = extract_metadonnees(rd.file.path, rd.url)

    if request.method == 'POST':
        form = MetadataEditForm(request.POST)
        if form.is_valid():
            for field, new_value in form.cleaned_data.items():
                old_value = metadata.get(field)
                if str(old_value) != str(new_value):
                    MetadataLog.objects.create(
                        document=rd,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        modified_by=request.user
                    )
                    metadata[field] = new_value
            success = True
        else:
            success = False
    else:
        form = MetadataEditForm(initial=metadata)
        success = False

    logs = MetadataLog.objects.filter(document=rd).order_by('-modified_at')
    return render(request, 'rawdocs/edit_metadata.html', {
        'form':     form,
        'metadata': metadata,
        'doc':      rd,
        'logs':     logs,
        'success':  success,
    })
