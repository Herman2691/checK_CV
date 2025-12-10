"""
Heck CV - Application d'analyse de CV avec Mistral AI
"""

from dotenv import load_dotenv
load_dotenv()  # Charger les variables d'environnement depuis .env

import streamlit as st
import os
from mistralai import Mistral
import json
from typing import List, Dict
import io
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Heck CV - Analyseur de CV",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(to bottom right, #f8f9ff, #f0f4ff);
    }
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #f8f9ff;
    }
    .score-excellent {
        background-color: #d4edda;
        color: #155724;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .score-bon {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .score-moyen {
        background-color: #fff3cd;
        color: #856404;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .score-faible {
        background-color: #f8d7da;
        color: #721c24;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialisation de Mistral AI
@st.cache_resource
def init_mistral():
    """Initialise le client Mistral AI"""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        st.error("⚠️ Clé API Mistral non trouvée. Veuillez configurer MISTRAL_API_KEY dans le fichier .env")
        st.stop()
    return Mistral(api_key=api_key)

def extract_text_from_file(uploaded_file) -> str:
    """Extrait le texte d'un fichier uploadé"""
    try:
        if uploaded_file.type == "text/plain":
            return uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import docx
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier {uploaded_file.name}: {str(e)}")
        return ""

def analyze_cv_with_mistral(client: Mistral, job_description: str, cv_content: str, cv_name: str) -> Dict:
    """Analyse un CV avec Mistral AI"""
    
    prompt = f"""Tu es un expert en recrutement. Analyse ce CV par rapport à l'offre d'emploi et réponds UNIQUEMENT avec un JSON valide (sans markdown, sans backticks).

Offre d'emploi:
{job_description}

CV du candidat ({cv_name}):
{cv_content}

Analyse le CV et fournis:
1. Un score de 0 à 100 représentant l'adéquation du candidat avec le poste
2. 3 à 5 points forts du candidat
3. 3 à 5 points à améliorer
4. 3 à 5 recommandations concrètes pour améliorer le CV

Format de réponse (JSON strict, sans texte avant ou après):
{{
  "score": <nombre entre 0 et 100>,
  "points_forts": ["point1", "point2", "point3"],
  "points_amelioration": ["point1", "point2", "point3"],
  "recommandations": ["rec1", "rec2", "rec3"]
}}"""

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        # Extraction du contenu
        content = response.choices[0].message.content
        
        # Nettoyage du contenu (enlever les balises markdown si présentes)
        content = content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Parse le JSON
        result = json.loads(content)
        
        return {
            "score": result.get("score", 0),
            "points_forts": result.get("points_forts", []),
            "points_amelioration": result.get("points_amelioration", []),
            "recommandations": result.get("recommandations", [])
        }
        
    except json.JSONDecodeError as e:
        st.warning(f"Erreur de parsing JSON pour {cv_name}. Utilisation de valeurs par défaut.")
        return {
            "score": 50,
            "points_forts": ["Profil intéressant"],
            "points_amelioration": ["CV à approfondir"],
            "recommandations": ["Détailler davantage les expériences"]
        }
    except Exception as e:
        st.error(f"Erreur lors de l'analyse de {cv_name}: {str(e)}")
        return None

def get_score_badge(score: int) -> str:
    """Retourne le badge HTML selon le score"""
    if score >= 80:
        return f'<span class="score-excellent">⭐ Excellent - {score}%</span>'
    elif score >= 60:
        return f'<span class="score-bon">✓ Bon - {score}%</span>'
    elif score >= 40:
        return f'<span class="score-moyen">○ Moyen - {score}%</span>'
    else:
        return f'<span class="score-faible">⚠ Faible - {score}%</span>'

def main():
    # Header
    st.markdown("""
        <h1 style='text-align: center; color: #667eea;'>
            🎯 Heck CV
        </h1>
        <h3 style='text-align: center; color: #764ba2;'>
            Analyse intelligente de CV avec Mistral AI
        </h3>
        <hr style='margin: 30px 0;'>
    """, unsafe_allow_html=True)
    
    # Initialisation du client Mistral
    client = init_mistral()
    
    # Sidebar pour les instructions
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Importez l'offre d'emploi** (TXT, PDF, DOCX)
        2. **Importez les CV** (jusqu'à 100 fichiers)
        3. **Cliquez sur "Analyser"** pour lancer l'analyse
        4. **Consultez les résultats** classés par score
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        st.info("Clé API Mistral chargée depuis .env")
        
        st.markdown("---")
        st.markdown("### 📊 Statistiques")
        if 'results' in st.session_state and st.session_state.results:
            total = len(st.session_state.results)
            excellent = sum(1 for r in st.session_state.results if r['score'] >= 80)
            bon = sum(1 for r in st.session_state.results if 60 <= r['score'] < 80)
            moyen = sum(1 for r in st.session_state.results if 40 <= r['score'] < 60)
            faible = sum(1 for r in st.session_state.results if r['score'] < 40)
            
            st.metric("Total candidats", total)
            st.metric("Excellent (80%+)", excellent)
            st.metric("Bon (60-79%)", bon)
            st.metric("Moyen (40-59%)", moyen)
            st.metric("Faible (<40%)", faible)
    
    # Section principale
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Offre d'emploi")
        job_file = st.file_uploader(
            "Importez l'offre d'emploi",
            type=["txt", "pdf", "docx"],
            key="job_upload",
            help="Formats acceptés: TXT, PDF, DOCX"
        )
        
        if job_file:
            job_description = extract_text_from_file(job_file)
            st.session_state['job_description'] = job_description
            st.success(f"✅ Offre chargée: {job_file.name}")
            with st.expander("Aperçu de l'offre"):
                st.text_area("Contenu", job_description[:500] + "...", height=150, disabled=True)
    
    with col2:
        st.markdown("### 👥 CV des candidats")
        cv_files = st.file_uploader(
            "Importez les CV (max 100)",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            key="cv_upload",
            help="Formats acceptés: TXT, PDF, DOCX"
        )
        
        if cv_files:
            if len(cv_files) > 100:
                st.error("⚠️ Maximum 100 CV autorisés")
                cv_files = cv_files[:100]
            st.session_state['cv_files'] = cv_files
            st.success(f"✅ {len(cv_files)} CV chargés")
    
    # Bouton d'analyse
    st.markdown("---")
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        analyze_button = st.button(
            "🚀 Analyser les CV",
            type="primary",
            use_container_width=True,
            disabled=not (st.session_state.get('job_description') and st.session_state.get('cv_files'))
        )
    
    # Analyse
    if analyze_button:
        job_description = st.session_state.get('job_description')
        cv_files = st.session_state.get('cv_files')
        
        if not job_description or not cv_files:
            st.error("⚠️ Veuillez charger une offre d'emploi et au moins un CV")
            return
        
        st.markdown("---")
        st.markdown("### 🔄 Analyse en cours...")
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, cv_file in enumerate(cv_files):
            status_text.text(f"Analyse de {cv_file.name}... ({idx + 1}/{len(cv_files)})")
            
            cv_content = extract_text_from_file(cv_file)
            if cv_content:
                analysis = analyze_cv_with_mistral(client, job_description, cv_content, cv_file.name)
                if analysis:
                    results.append({
                        'name': cv_file.name,
                        'score': analysis['score'],
                        'points_forts': analysis['points_forts'],
                        'points_amelioration': analysis['points_amelioration'],
                        'recommandations': analysis['recommandations']
                    })
            
            progress_bar.progress((idx + 1) / len(cv_files))
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['score'], reverse=True)
        st.session_state['results'] = results
        
        status_text.text("✅ Analyse terminée!")
        st.balloons()
    
    # Affichage des résultats
    if 'results' in st.session_state and st.session_state.results:
        st.markdown("---")
        st.markdown("## 📊 Résultats de l'analyse")
        
        for idx, result in enumerate(st.session_state.results):
            with st.container():
                st.markdown(f"""
                    <div style='background: white; padding: 20px; border-radius: 10px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h3 style='color: #667eea;'>#{idx + 1} - {result['name']}</h3>
                        {get_score_badge(result['score'])}
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### ✅ Points forts")
                    for point in result['points_forts']:
                        st.markdown(f"- {point}")
                
                with col2:
                    st.markdown("#### ⚠️ À améliorer")
                    for point in result['points_amelioration']:
                        st.markdown(f"- {point}")
                
                with col3:
                    st.markdown("#### 💡 Recommandations")
                    for rec in result['recommandations']:
                        st.markdown(f"- {rec}")
                
                st.markdown("---")
        
        # Export des résultats
        if st.button("📥 Exporter les résultats (JSON)"):
            export_data = {
                "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre_candidats": len(st.session_state.results),
                "resultats": st.session_state.results
            }
            st.download_button(
                label="Télécharger JSON",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=f"heck_cv_resultats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()