import re
import json
import requests
from pathlib import Path
from urllib.parse import urlparse

import spacy
from PyPDF2 import PdfReader
from langdetect import detect

# Chargez une fois :
NLP_FR = spacy.load("fr_core_news_sm")
NLP_EN = spacy.load("en_core_web_sm")

# Stopwords FR/EN basiques pour nettoyage
STOPWORDS = {
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "en", "à", "dans", "que", "qui",
    "pour", "par", "sur", "avec", "au", "aux", "ce", "ces", "se", "ses", "est",
    "the", "and", "of", "to", "in", "that", "it", "is", "was", "for", "on", "are", "with",
    "as", "i", "at", "be", "by", "this"
}


def call_mistral_extraction(text_chunk, document_url=""):
    """
    Uses Mistral AI for intelligent metadata extraction via direct API
    """
    # 🔑 YOUR MISTRAL API KEY
    MISTRAL_API_KEY = "oKdjCl98ACUqpUc4TCyqcfZFMzNNdapl"

    try:
        url = "https://api.mistral.ai/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MISTRAL_API_KEY}"
        }

        prompt = f"""
        Analyze this document and extract metadata with MAXIMUM PRECISION:

        DOCUMENT TEXT (first 2000 chars):
        {text_chunk[:2000]}

        SOURCE URL: {document_url}

        TASK: Extract metadata and return ONLY a valid JSON object with these exact keys:
        {{
            "title": "the ACTUAL document title from the text",
            "type": "guideline|regulation|directive|report|procedure|standard|other - look in title/content",
            "publication_date": "exact date from document (DD Month YYYY format)",
            "version": "document version/revision if mentioned",
            "source": "issuing organization like European Commission, EMA, FDA - check URL domain and text",
            "context": "main domain/subject area (pharmaceutical, medical, legal, etc.)",
            "country": "country code (EU, US, etc.)",
            "language": "document language (en, fr, etc.)"
        }}

        INSTRUCTIONS:
        - For SOURCE: Look at URL '{document_url}' - if eur-lex.europa.eu then "European Commission"
        - For TYPE: Look for words like "guideline", "regulation", "directive" in the title
        - Extract exact publication date like "24 November 2008"
        - Return ONLY the JSON object, no other text
        """

        data = {
            "model": "mistral-large-latest",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            response_text = result['choices'][0]['message']['content']

            # Try to parse JSON
            try:
                # Find JSON in response (in case there's extra text)
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    metadata = json.loads(json_str)
                    print("✅ Mistral extraction successful!")
                    return metadata
                else:
                    print("❌ No JSON found in Mistral response")
                    print(f"Raw response: {response_text}")
                    return None
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print(f"Raw response: {response_text}")
                return None
        else:
            print(f"❌ Mistral API error: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"❌ Mistral API error: {e}")
        return None


def extract_full_text(file_path: str) -> str:
    """Lit tout le PDF, nettoie et enlève les stopwords."""
    reader = PdfReader(file_path)
    pages = [p.extract_text() or "" for p in reader.pages]
    text = " ".join(pages)
    text = re.sub(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ\s\.,;:\-'\(\)]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    return " ".join(w for w in words if w.lower() not in STOPWORDS)


def extract_basic_metadata(file_path: str, source_url: str) -> dict:
    """Fallback basic extraction (your original code)"""
    reader = PdfReader(file_path)
    info = reader.metadata or {}
    title = info.title or ""

    full_text = extract_full_text(file_path)

    # Basic language detection
    try:
        lang = detect(full_text)
    except:
        lang = "fr"

    # Basic patterns (simplified)
    extracted_title = title or Path(file_path).stem

    # TLD-based country
    tld = urlparse(source_url).netloc.split('.')[-1].upper()
    country = tld if len(tld) == 2 else ""

    return {
        "title": extracted_title,
        "document_type": "autres",
        "publication_date": "",
        "version": "",
        "source_organization": "",
        "context": "",
        "country": country,
        "language": lang,
    }


def extract_metadonnees(file_path: str, source_url: str) -> dict:
    """
    Main extraction function - tries Mistral AI first, falls back to basic
    """
    print("🔍 Starting metadata extraction...")

    # Get full text for processing
    full_text = extract_full_text(file_path)

    # Try Mistral AI extraction first
    mistral_result = call_mistral_extraction(full_text, source_url)

    if mistral_result:
        print("✅ Using Mistral AI extraction")

        # Post-process to ensure consistent EMA for European docs
        if mistral_result.get("source") in ["European Commission", "Commission", "EU Commission"]:
            mistral_result["source"] = "EMA"

        # If version is empty, try to extract from title or content
        if not mistral_result.get("version"):
            version_patterns = [
                r'(\d{4}\s+C\s+\d+\s+\d+)',  # 2013 C 223 01
                r'(v\d+\.\d+)',  # v1.0
                r'(version\s+\d+)',  # version 1
                r'(\d+/\d+/[A-Z]+)',  # regulatory patterns
            ]
            full_text_sample = text_chunk[:1000]  # First 1000 chars
            for pattern in version_patterns:
                match = re.search(pattern, full_text_sample, re.IGNORECASE)
                if match:
                    mistral_result["version"] = match.group(1)
                    break

        # Add URL source to the result
        mistral_result["url_source"] = source_url
        return mistral_result
    else:
        print("⚠️  Falling back to basic extraction")
        # Use basic extraction as fallback
        basic_result = extract_basic_metadata(file_path, source_url)
        basic_result["url_source"] = source_url
        return basic_result