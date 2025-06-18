# rawdocs/utils.py
import json
from PyPDF2 import PdfReader
from langdetect import detect
from urllib.parse import urlparse

def extract_metadata(file_path, source_url):
    reader = PdfReader(file_path)
    info = reader.metadata or {}

    # 1) Métadonnées internes PDF
    title = info.title or ''
    date  = info.creation_date or ''

    # 2) Version du PDF (header)
    version = getattr(reader, "pdf_header_version", "")

    # 3) Détection de la langue sur les premières pages
    text = ""
    for page in reader.pages[:3]:
        text += page.extract_text() or ""
    try:
        language = detect(text)
    except:
        language = ""

    # 4) Pays — on le déduit du TLD du domaine source
    domain = urlparse(source_url).netloc
    tld = domain.split('.')[-1]
    country = tld.upper() if len(tld) == 2 else ''

    return {
        "title":    title,
        "date":     date,
        "language": language,
        "country":  country,
        "source":   source_url,
        "version":  version,
    }


import requests

OLLAMA_URL = "http://localhost:11434"

def call_mistral(prompt: str, max_tokens: int = 200000) -> str:
    """
    Envoie un prompt à Mistral via Ollama et renvoie la réponse textuelle.
    """
    resp = requests.post(
        f"{OLLAMA_URL}/v1/completions/mistral",
        json={
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.0,
        }
    )
    resp.raise_for_status()
    # Selon la version de l’API Ollama, le champ peut être 'choices'[0]['message']['content']
    data = resp.json()
    return data["choices"][0]["message"]["content"]
