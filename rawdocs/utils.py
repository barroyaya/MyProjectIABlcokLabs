import re
import requests
from PyPDF2 import PdfReader
from langdetect import detect
from urllib.parse import urlparse

# URL de votre service Ollama/Mistral
OLLAMA_URL = "http://localhost:11434"

# Stopwords FR/EN basiques
STOPWORDS = {
    "le","la","les","de","des","du","un","une","et","en","à","dans","que","qui",
    "pour","par","sur","avec","au","aux","ce","ces","se","ses","est",
    "the","and","of","to","in","that","it","is","was","for","on","are","with",
    "as","I","at","be","by","this"
}

def call_mistral(prompt: str, max_tokens: int = 200000) -> str:
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/v1/completions/mistral",
            json={"prompt": prompt, "max_tokens": max_tokens, "temperature": 0.0},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""

def extract_full_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    raw = []
    for page in reader.pages:
        raw.append(page.extract_text() or "")
    text = "\n".join(raw)
    # nettoyage basique
    text = re.sub(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ\s\.,;:\-'\(\)]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # retirer stopwords
    words = text.split()
    return " ".join(w for w in words if w.lower() not in STOPWORDS)

def extract_metadonnees(file_path: str, source_url: str) -> dict:
    reader = PdfReader(file_path)
    info    = reader.metadata or {}
    # PDF interne
    title   = info.title or ""
    version = getattr(reader, "pdf_header_version", "")

    # texte complet nettoyé
    full_text = extract_full_text(file_path)

    # détection langue
    try:
        language = detect(full_text)
    except:
        language = ""

    # pays via TLD
    domain  = urlparse(source_url).netloc
    tld     = domain.split(".")[-1]
    country = tld.upper() if len(tld) == 2 else ""

    # URL brute
    url_source = source_url

    # prompts détaillés
    # 1) Type de document
    prompt_type = (
        "Tu es un métadonneur expert. En te basant sur le texte qui suit, "
        "détermine s'il s'agit d'un « Rapport » ou d'un « Contrat ». "
        "Réponds uniquement par Rapport ou Contrat.\n\n"
        f"{full_text[:5000]}"
    )
    doc_type = call_mistral(prompt_type)

    # 2) Date de publication
    match = re.search(r"(?i)(?:Publié\s+le|Publication\s*[:\-]?)\s*([0-3]?\d\s+\w+\s+\d{4})", full_text)
    if match:
        date_pub = match.group(1)
    else:
        prompt_date = (
            "Tu es un métadonneur. Extrait la date de publication (ex. « 12 mai 2023 ») "
            "du texte suivant ou renvoie une chaîne vide.\n\n"
            f"{full_text[:5000]}"
        )
        date_pub = call_mistral(prompt_date)

    # 3) Source interne (EMA/FDA…)
    prompt_source = (
        "Tu es un métadonneur. Quelle entité est citée comme source (ex. EMA, FDA, etc.) ? "
        "Réponds uniquement par le nom ou renvoie vide si aucune.\n\n"
        f"{full_text[:5000]}"
    )
    source_name = call_mistral(prompt_source)

    # 4) Contexte / résumé
    prompt_context = (
        "Tu es un métadonneur. Fournis un bref résumé du contexte et de l’objectif de ce document "
        "en te basant sur son contenu.\n\n"
        f"{full_text[:10000]}"
    )
    context = call_mistral(prompt_context)

    return {
        "title":            title,
        "type":             doc_type,
        "language":         language,
        "version":          version,
        "url_source":       url_source,
        "source":           source_name,
        "publication_date": date_pub,
        "context":          context,
        "country":          country,
    }
