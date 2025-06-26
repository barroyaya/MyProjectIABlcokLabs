# rawdocs/models.py

from os.path import join
from datetime import datetime
from django.db import models
from django.conf import settings

def pdf_upload_to(instance, filename):
    """
    Place chaque PDF téléchargé dans un sous-dossier horodaté.
    Ex. "20250626_143502/mon_document.pdf"
    """
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return join(ts, filename)

class RawDocument(models.Model):
    url        = models.URLField(help_text="URL d'origine du PDF")
    file       = models.FileField(upload_to=pdf_upload_to, help_text="Fichier PDF téléchargé")
    created_at = models.DateTimeField(auto_now_add=True)

    # On autorise NULL/blank pour ne pas casser les anciens enregistrements
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='raw_documents',
        null=True,
        blank=True,
        help_text="Utilisateur qui a téléchargé ce document"
    )

    def __str__(self):
        owner_name = self.owner.username if self.owner else "–"
        return f"PDF #{self.pk} ({self.url}) – par {owner_name}"
