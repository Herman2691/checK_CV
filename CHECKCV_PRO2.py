"""
CHECK CV - Application d'analyse de CV avec IA
Design inspiré de l'interface Gemini (Épuré & Moderne)
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
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
import base64

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="CHECK CV - Analyseur de CV Professionnel",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DESIGN INSPIRÉ DE GEMINI (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Inter:wght@300;400;500;600&display=swap');
    
    * { font-family: 'Inter', 'Google Sans', sans-serif; }

    /* Fond principal (Gris très clair Gemini) */
    .stApp { background-color: #f8f9fa; }
    
    /* Header principal style "Google" */
    .professional-header {
        background: white;
        padding: 40px 30px; 
        border-radius: 24px; 
        margin-bottom: 30px;
        border: 1px solid #e3e3e3;
        text-align: center;
    }
    
    .professional-header h1 {
        color: #1f1f1f; 
        font-size: 2.8em; 
        font-weight: 500; 
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .professional-header p { 
        color: #444746; 
        font-size: 1.1em; 
        margin-top: 10px; 
    }

    /* Cartes d'upload et de résultats */
    .upload-card, .result-card {
        background: white; 
        border-radius: 24px; 
        padding: 25px;
        border: 1px solid #e3e3e3;
        transition: all 0.2s ease;
        margin-bottom: 20px;
    }

    .result-card:hover {
        background-color: #f1f3f4;
        border-color: #c1c1c1;
    }

    .card-header h3 { 
        color: #1f1f1f; 
        font-size: 1.4em; 
        font-weight: 500; 
        margin: 0; 
    }

    /* Score et Badges */
    .score-number {
        font-size: 3em; 
        font-weight: 500;
        color: #0b57d0; /* Bleu Google */
        line-height: 1;
    }

    /* Sections d'analyse avec couleurs douces */
    .analysis-section {
        border-radius: 16px; 
        padding: 20px;
        margin-top: 15px;
        border: 1px solid transparent;
        height: 100%;
    }
    
    .section-strengths { background-color: #e8f0fe; border-color: #d2e3fc; color: #174ea6; } 
    .section-improvements { background-color: #fef7e0; border-color: #feefc3; color: #b06000; }
    .section-recommendations { background-color: #f1f3f4; border-color: #e3e3e3; color: #1f1f1f; }

    .analysis-section h4 { font-weight: 600; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }

    /* Boutons style Google (Pilule) */
    .stButton > button {
        background-color: #0b57d0 !important;
        color: white !important;
        border-radius: 100px !important;
        padding: 14px 32px !important;
        border: none !important;
        font-weight: 500 !important;
        transition: background-color 0.2s !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }

    .stButton > button:hover {
        background-color: #0842a0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }

    /* Sidebar et Stats */
    .stat-card {
        background: #0b57d0; 
        color: white;
        padding: 20px; 
        border-radius: 16px; 
        margin-bottom: 10px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

@st.cache_resource
def init_mistral():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        st.error("⚠️ Clé API Mistral non trouvée.")
        st.stop()
    return MistralClient(api_key=api_key)

def extract_text_from_file(uploaded_file) -> str:
    try:
        if uploaded_file.type == "text/plain":
            return uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            return "".join([page.extract_text() for page in pdf_reader.pages])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import docx
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            return "\n".join([p.text for p in doc.paragraphs])
        return ""
    except Exception as e:
        st.error(f"Erreur lecture {uploaded_file.name}: {e}")
        return ""

def analyze_cv_with_mistral(client: MistralClient, job_description: str, cv_content: str, cv_name: str) -> dict:
    prompt = f"""Tu es un expert RH. Analyse ce CV par rapport au poste. Réponds EXCLUSIVEMENT en JSON.
    Poste: {job_description}
    CV ({cv_name}): {cv_content}
    JSON format:
    {{
      "nom_complet": "NOM Prénom",
      "score": 85,
      "points_forts": ["..."],
      "points_amelioration": ["..."],
      "recommandations": ["..."]
    }}"""

    try:
        from mistralai.models.chat_completion import ChatMessage
        response = client.chat(
            model="mistral-large-latest",
            messages=[ChatMessage(role="user", content=prompt)],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        return None

# --- INTERFACE PRINCIPALE ---

def main():
    st.markdown('<div class="professional-header"><h1>CHECK CV</h1><p>Analyse intelligente propulsée par l\'IA</p></div>', unsafe_allow_html=True)
    
    client = init_mistral()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="upload-card"><h3>📄 Offre d\'emploi</h3>', unsafe_allow_html=True)
        job_file = st.file_uploader("Upload job", type=["txt", "pdf", "docx"], label_visibility="collapsed")
        if job_file:
            st.session_state['job_text'] = extract_text_from_file(job_file)
            st.success("Offre prête")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="upload-card"><h3>👥 CV Candidats</h3>', unsafe_allow_html=True)
        cv_files = st.file_uploader("Upload CVs", type=["txt", "pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed")
        if cv_files:
            st.session_state['cv_files'] = cv_files
            st.success(f"{len(cv_files)} CV(s) prêt(s)")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 LANCER L'ANALYSE", use_container_width=True):
        if 'job_text' in st.session_state and cv_files:
            results = []
            progress = st.progress(0)
            for i, f in enumerate(cv_files):
                res = analyze_cv_with_mistral(client, st.session_state['job_text'], extract_text_from_file(f), f.name)
                if res:
                    res['filename'] = f.name
                    results.append(res)
                progress.progress((i + 1) / len(cv_files))
            
            st.session_state['results'] = sorted(results, key=lambda x: x['score'], reverse=True)
            st.rerun()

    if 'results' in st.session_state:
        for idx, r in enumerate(st.session_state['results']):
            st.markdown(f"""
            <div class="result-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 class="candidate-name">{r['nom_complet']}</h3>
                        <p class="candidate-file">Fichier : {r['filename']}</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="score-number">{r['score']}%</div>
                        <div style="color: #444746; font-size: 0.8em;">MATCH</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown('<div class="analysis-section section-strengths"><h4>✅ Points Forts</h4>', unsafe_allow_html=True)
                for p in r['points_forts']: st.write(f"• {p}")
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="analysis-section section-improvements"><h4>⚠️ À Améliorer</h4>', unsafe_allow_html=True)
                for p in r['points_amelioration']: st.write(f"• {p}")
                st.markdown('</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="analysis-section section-recommendations"><h4>💡 Conseils</h4>', unsafe_allow_html=True)
                for p in r['recommandations']: st.write(f"• {p}")
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
