from django import forms

class URLForm(forms.Form):
    pdf_url = forms.URLField(
        label="URL du PDF",
        widget=forms.URLInput(attrs={
            'class': 'input',
            'placeholder': 'Entrez l’URL du PDF',
            'id': 'id_pdf_url',
        })
    )
