from django import forms

class URLForm(forms.Form):
    pdf_url = forms.URLField(label="URL du PDF", widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://.../document.pdf'
    }))
