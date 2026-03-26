"""
CHECK CV - Version Finale Corrigée
Correction de l'affichage (JSON imbriqué) + Design Gemini
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from mistralai.client import MistralClient
import json
from typing import List, Dict
import io
from datetime import datetime
import time
import base64

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="CHECK CV - Analyseur Pro",
    page_icon="✨",
    layout="wide"
)

# --- STYLE CSS (DESIGN GEMINI + TEXTE BLANC) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Inter:wght@300;400;500;600&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8f9fa; }
    
    .professional-header {
        background: white; padding: 40px; border-radius: 24px; 
        margin-bottom: 30px; border: 1px solid #e3e3e3; text-align: center;
    }
    .professional-header h1 { color: #1f1f1f; font-size: 2.5em; font-weight: 500; margin: 0; }

    .upload-card, .result-card {
        background: white; border-radius: 24px; padding: 25px;
        border: 1px solid #e3e3e3; margin-bottom: 20px;
    }

    .score-number { font-size: 3em; font-weight: 500; color: #0b57d0; line-height: 1; }

    /* SECTIONS DE RÉSULTATS - FORÇAGE BLANC */
    .analysis-section {
        border-radius: 16px; padding: 20px; margin-top: 15px;
        height: 100%; color: #ffffff !important;
    }
    .section-strengths { background-color: #1a73e8; } 
    .section-improvements { background-color: #f9ab00; }
    .section-recommendations { background-color: #34a853; }

    .analysis-section h4 { color: #ffffff !important; text-transform: uppercase; font-size: 0.9em; letter-spacing: 1px; margin-bottom: 15px; }
    .analysis-section p, .analysis-section li { color: #ffffff !important; font-size: 0.95em; line-height: 1.5; margin-bottom: 8px; }

    .stButton > button {
        background-color: #0b57d0 !important; color: white !important;
        border-radius: 100px !important; padding: 12px 30px !important;
        width: 100%; border: none !important; font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE MISTRAL ---

@st.cache_resource
def init_mistral():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        st.error("Clé API manquante")
        st.stop()
    return MistralClient(api_key=api_key)

def extract_text(file) -> str:
    try:
        if file.type == "application/pdf":
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
            return "".join([p.extract_text() for p in reader.pages])
        return file.getvalue().decode("utf-8")
    except: return ""

def analyze_cv(client, job, cv_txt, name):
    # Prompt forçant un format simple pour éviter les dictionnaires complexes
    prompt = f"""Analyse ce CV pour le poste. Réponds UNIQUEMENT en JSON.
    IMPORTANT: 'points_forts', 'points_amelioration' et 'recommandations' doivent être des listes de CHAINES DE CARACTERES simples (pas d'objets {}).
    
    Poste: {job}
    CV: {cv_txt}
    
    Format:
    {{
      "nom_complet": "Nom",
      "score": 80,
      "points_forts": ["Phrase 1", "Phrase 2"],
      "points_amelioration": ["Phrase 1"],
      "recommandations": ["Phrase 1"]
    }}"""
    
    try:
        from mistralai.models.chat_completion import ChatMessage
        resp = client.chat(model="mistral-large-latest", messages=[ChatMessage(role="user", content=prompt)])
        content = resp.choices[0].message.content
        if "
http://googleusercontent.com/immersive_entry_chip/0

### Ce qui a été corrigé :
1.  **Nettoyage des Accolades `{...}`** : J'ai ajouté une vérification `isinstance(item, dict)`. Si l'IA renvoie un dictionnaire, le code extrait automatiquement le texte caché dans 'details' ou 'action'.
2.  **Prompt Amélioré** : J'ai ajouté une consigne stricte à l'IA pour qu'elle renvoie des phrases simples, ce qui évitera le problème à la source.
3.  **Texte Blanc Garanti** : Le CSS force maintenant le blanc sur tous les éléments (`p`, `li`, `h4`) à l'intérieur des zones de résultats.
4.  **Stabilité** : Ajout de vérifications pour éviter que l'application ne plante si un fichier est mal lu.

Souhaitez-vous que je rajoute une option pour comparer deux candidats côte à côte ?
