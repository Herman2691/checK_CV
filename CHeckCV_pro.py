"""
CHECK CV - Application d'analyse de CV avec AI
Version Professionnelle
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from mistralai import Mistral
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Configuration de la page
st.set_page_config(
    page_title=" CHECK CV - Analyseur de CV Professionnel",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS professionnel personnalisé
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
    }
    
    .main {
        background: transparent;
    }
    
    /* Header personnalisé */
    .professional-header {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        padding: 40px 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    .professional-header h1 {
        color: white;
        font-size: 3.5em;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .professional-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.3em;
        margin-top: 10px;
        font-weight: 300;
    }
    
    /* Cards */
    .upload-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
        height: 100%;
    }
    
    .upload-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .card-header h3 {
        color: #0083b0;
        font-size: 1.5em;
        font-weight: 700;
        margin: 0;
    }
    
    .icon-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    
    .icon-job {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
    }
    
    .icon-cv {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    /* Upload box */
    .upload-box {
        border: 3px dashed #00b4db;
        border-radius: 15px;
        padding: 40px 20px;
        text-align: center;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-box:hover {
        border-color: #0083b0;
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        transform: scale(1.02);
    }
    
    /* Success box */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 5px 15px rgba(40, 167, 69, 0.2);
    }
    
    .success-box-icon {
        font-size: 24px;
        margin-right: 10px;
    }
    
    /* Result cards */
    .result-card {
        background: white;
        border-radius: 20px;
        padding: 35px;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 6px solid #00b4db;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateX(10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .candidate-info {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .rank-badge {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        font-weight: 800;
        box-shadow: 0 5px 15px rgba(0, 180, 219, 0.4);
    }
    
    .candidate-name {
        font-size: 1.8em;
        font-weight: 700;
        color: #0083b0;
        margin: 0;
    }
    
    .candidate-file {
        font-size: 0.9em;
        color: #888;
        margin-top: 5px;
    }
    
    .score-display {
        text-align: right;
    }
    
    .score-number {
        font-size: 3.5em;
        font-weight: 800;
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    .score-label {
        font-size: 0.9em;
        color: #888;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Score badges */
    .score-excellent {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 10px 25px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1em;
        display: inline-block;
        box-shadow: 0 5px 15px rgba(21, 87, 36, 0.2);
        border: 2px solid #28a745;
    }
    
    .score-bon {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 10px 25px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1em;
        display: inline-block;
        box-shadow: 0 5px 15px rgba(12, 84, 96, 0.2);
        border: 2px solid #17a2b8;
    }
    
    .score-moyen {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 10px 25px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1em;
        display: inline-block;
        box-shadow: 0 5px 15px rgba(133, 100, 4, 0.2);
        border: 2px solid #ffc107;
    }
    
    .score-faible {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 10px 25px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1em;
        display: inline-block;
        box-shadow: 0 5px 15px rgba(114, 28, 36, 0.2);
        border: 2px solid #dc3545;
    }
    
    /* Analysis sections */
    .analysis-section {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 25px;
        margin-top: 20px;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .analysis-section h4 {
        font-size: 1.2em;
        font-weight: 700;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-strengths {
        background: linear-gradient(135deg, #d4edda 0%, #e8f5e9 100%);
        border-left: 4px solid #28a745;
    }
    
    .section-improvements {
        background: linear-gradient(135deg, #fff3cd 0%, #fff8e1 100%);
        border-left: 4px solid #ffc107;
    }
    
    .section-recommendations {
        background: linear-gradient(135deg, #d1ecf1 0%, #e1f5fe 100%);
        border-left: 4px solid #17a2b8;
    }
    
    .analysis-section ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .analysis-section li {
        padding: 12px 0;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        display: flex;
        align-items: start;
        gap: 12px;
        font-size: 1em;
        line-height: 1.6;
    }
    
    .analysis-section li:last-child {
        border-bottom: none;
    }
    
    .bullet {
        font-size: 1.3em;
        font-weight: 700;
        flex-shrink: 0;
        margin-top: 2px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        border: none;
        padding: 18px 50px;
        font-size: 1.2em;
        font-weight: 700;
        border-radius: 50px;
        box-shadow: 0 10px 30px rgba(0, 180, 219, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0, 180, 219, 0.6);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Stats cards in sidebar */
    .stat-card {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0, 180, 219, 0.3);
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: 800;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.9em;
        opacity: 0.9;
        margin-top: 5px;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .result-card {
        animation: fadeIn 0.5s ease;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
1. Le NOM et PRÉNOM complet du candidat (extrait du CV)
2. Un score de 0 à 100 représentant l'adéquation du candidat avec le poste
3. 3 à 5 points forts du candidat
4. 3 à 5 points à améliorer
5. 3 à 5 recommandations concrètes pour améliorer le CV

Format de réponse (JSON strict, sans texte avant ou après):
{{
  "nom_complet": "Prénom NOM du candidat",
  "score": <nombre entre 0 et 100>,
  "points_forts": ["point1", "point2", "point3"],
  "points_amelioration": ["point1", "point2", "point3"],
  "recommandations": ["rec1", "rec2", "rec3"]
}}"""

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        result = json.loads(content)
        
        return {
            "nom_complet": result.get("nom_complet", "Nom non trouvé"),
            "score": result.get("score", 0),
            "points_forts": result.get("points_forts", []),
            "points_amelioration": result.get("points_amelioration", []),
            "recommandations": result.get("recommandations", [])
        }
        
    except json.JSONDecodeError:
        return {
            "nom_complet": "Nom non trouvé",
            "score": 50,
            "points_forts": ["Profil intéressant"],
            "points_amelioration": ["CV à approfondir"],
            "recommandations": ["Détailler davantage les expériences"]
        }
    except Exception as e:
        st.error(f"Erreur lors de l'analyse de {cv_name}: {str(e)}")
        return None

def generate_pdf_report(results: List[Dict], job_description: str) -> bytes:
    """Génère un rapport PDF des résultats"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                           topMargin=2*cm, bottomMargin=2*cm)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#00b4db'),
        spaceAfter=30,
        alignment=1  # Centré
    )
    
    # Style pour les en-têtes
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0083b0'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Titre du rapport
    story.append(Paragraph("🎯 CHECK CV - RAPPORT D'ANALYSE", title_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Résumé
    story.append(Paragraph("RÉSUMÉ DE L'ANALYSE", header_style))
    summary_data = [
        ['Nombre de candidats analysés:', str(len(results))],
        ['Excellent (80%+):', str(sum(1 for r in results if r['score'] >= 80))],
        ['Bon (60-79%):', str(sum(1 for r in results if 60 <= r['score'] < 80))],
        ['Moyen (40-59%):', str(sum(1 for r in results if 40 <= r['score'] < 60))],
        ['Faible (<40%):', str(sum(1 for r in results if r['score'] < 40))],
    ]
    
    summary_table = Table(summary_data, colWidths=[12*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#00b4db'))
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 1*cm))
    
    # Détails des candidats
    for idx, result in enumerate(results):
        if idx > 0:
            story.append(PageBreak())
        
        # Rang et nom
        story.append(Paragraph(f"CANDIDAT #{idx + 1}", header_style))
        story.append(Paragraph(f"<b>Nom:</b> {result['nom_complet']}", styles['Normal']))
        story.append(Paragraph(f"<b>Fichier:</b> {result['filename']}", styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
        
        # Score
        score_color = '#28a745' if result['score'] >= 80 else '#17a2b8' if result['score'] >= 60 else '#ffc107' if result['score'] >= 40 else '#dc3545'
        score_text = f"<b>Score d'adéquation: <font color='{score_color}'>{result['score']}%</font></b>"
        story.append(Paragraph(score_text, styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Points forts
        story.append(Paragraph("✅ <b>POINTS FORTS</b>", header_style))
        for point in result['points_forts']:
            story.append(Paragraph(f"• {point}", styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
        
        # Points à améliorer
        story.append(Paragraph("⚠️ <b>POINTS À AMÉLIORER</b>", header_style))
        for point in result['points_amelioration']:
            story.append(Paragraph(f"• {point}", styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
        
        # Recommandations
        story.append(Paragraph("💡 <b>RECOMMANDATIONS</b>", header_style))
        for rec in result['recommandations']:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
    
    # Générer le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def get_score_badge(score: int) -> str:
    """Retourne le badge HTML selon le score"""
    if score >= 80:
        return f'<span class="score-excellent">⭐ EXCELLENT - {score}%</span>'
    elif score >= 60:
        return f'<span class="score-bon">✓ BON - {score}%</span>'
    elif score >= 40:
        return f'<span class="score-moyen">○ MOYEN - {score}%</span>'
    else:
        return f'<span class="score-faible">⚠ FAIBLE - {score}%</span>'

def main():
    # Professional Header
    st.markdown("""
        <div class="professional-header">
            <h1>🎯 HECK CV</h1>
            <p>Plateforme d'Analyse Intelligente de CV avec IA</p>
        </div>
    """, unsafe_allow_html=True)
    
    client = init_mistral()
    
    # Sidebar professionnel
    with st.sidebar:
        st.markdown("### 📋 GUIDE D'UTILISATION")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 20px; border-radius: 15px; border-left: 4px solid #00b4db;'>
        <ol style='margin: 0; padding-left: 20px;'>
            <li style='margin: 10px 0;'><strong>Importer</strong> l'offre d'emploi</li>
            <li style='margin: 10px 0;'><strong>Charger</strong> les CV candidats</li>
            <li style='margin: 10px 0;'><strong>Lancer</strong> l'analyse IA</li>
            <li style='margin: 10px 0;'><strong>Consulter</strong> les résultats</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### ⚙️ CONFIGURATION")
        st.success("✓ API Mistral connectée")
        
        if 'results' in st.session_state and st.session_state.results:
            st.markdown("---")
            st.markdown("### 📊 STATISTIQUES")
            
            total = len(st.session_state.results)
            excellent = sum(1 for r in st.session_state.results if r['score'] >= 80)
            bon = sum(1 for r in st.session_state.results if 60 <= r['score'] < 80)
            moyen = sum(1 for r in st.session_state.results if 40 <= r['score'] < 60)
            faible = sum(1 for r in st.session_state.results if r['score'] < 40)
            
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total}</div>
                <div class="stat-label">CANDIDATS ANALYSÉS</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Excellent", excellent, delta=None)
                st.metric("Moyen", moyen, delta=None)
            with col2:
                st.metric("Bon", bon, delta=None)
                st.metric("Faible", faible, delta=None)
    
    # Main content area
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="upload-card">
            <div class="card-header">
                <div class="icon-circle icon-job">📄</div>
                <h3>Offre d'Emploi</h3>
            </div>
        """, unsafe_allow_html=True)
        
        job_file = st.file_uploader(
            "Charger l'offre d'emploi",
            type=["txt", "pdf", "docx"],
            key="job_upload",
            label_visibility="collapsed"
        )
        
        if job_file:
            job_description = extract_text_from_file(job_file)
            st.session_state['job_description'] = job_description
            st.markdown(f"""
            <div class="success-box">
                <div style='display: flex; align-items: center;'>
                    <span class="success-box-icon">✓</span>
                    <div>
                        <strong>Offre chargée avec succès</strong><br>
                        <small>{job_file.name} • {len(job_description)} caractères</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="upload-card">
            <div class="card-header">
                <div class="icon-circle icon-cv">👥</div>
                <h3>CV Candidats</h3>
            </div>
        """, unsafe_allow_html=True)
        
        cv_files = st.file_uploader(
            "Charger les CV (max 100)",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            key="cv_upload",
            label_visibility="collapsed"
        )
        
        if cv_files:
            if len(cv_files) > 100:
                st.error("⚠️ Maximum 100 CV autorisés")
                cv_files = cv_files[:100]
            st.session_state['cv_files'] = cv_files
            st.markdown(f"""
            <div class="success-box">
                <div style='display: flex; align-items: center;'>
                    <span class="success-box-icon">✓</span>
                    <div>
                        <strong>{len(cv_files)} CV chargés</strong><br>
                        <small>Prêts pour l'analyse</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Analyze button
    st.markdown("<br>", unsafe_allow_html=True)
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        analyze_button = st.button(
            "🚀 LANCER L'ANALYSE",
            use_container_width=True,
            disabled=not (st.session_state.get('job_description') and st.session_state.get('cv_files'))
        )
    
    # Analysis process
    if analyze_button:
        job_description = st.session_state.get('job_description')
        cv_files = st.session_state.get('cv_files')
        
        st.markdown("---")
        st.markdown("### 🔄 ANALYSE EN COURS...")
        
        results = []
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        for idx, cv_file in enumerate(cv_files):
            status_container.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1);'>
                <h4 style='color: #00b4db; margin: 0;'>Analyse de {cv_file.name}</h4>
                <p style='color: #888; margin: 10px 0 0 0;'>Candidat {idx + 1} sur {len(cv_files)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            cv_content = extract_text_from_file(cv_file)
            if cv_content:
                analysis = analyze_cv_with_mistral(client, job_description, cv_content, cv_file.name)
                if analysis:
                    results.append({
                        'filename': cv_file.name,
                        'nom_complet': analysis['nom_complet'],
                        'score': analysis['score'],
                        'points_forts': analysis['points_forts'],
                        'points_amelioration': analysis['points_amelioration'],
                        'recommandations': analysis['recommandations']
                    })
            
            progress_bar.progress((idx + 1) / len(cv_files))
            time.sleep(0.1)
        
        results.sort(key=lambda x: x['score'], reverse=True)
        st.session_state['results'] = results
        
        status_container.success("✅ Analyse terminée avec succès!")
        st.balloons()
    
    # Results display
    if 'results' in st.session_state and st.session_state.results:
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; margin: 40px 0;'>
            <h2 style='color: white; font-size: 2.5em; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                📊 RÉSULTATS DE L'ANALYSE
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, result in enumerate(st.session_state.results):
            st.markdown(f"""
            <div class="result-card">
                <div class="result-header">
                    <div class="candidate-info">
                        <div class="rank-badge">#{idx + 1}</div>
                        <div>
                            <h3 class="candidate-name">{result['nom_complet']}</h3>
                            <p class="candidate-file">📄 {result['filename']}</p>
                        </div>
                    </div>
                    <div class="score-display">
                        <div class="score-number">{result['score']}%</div>
                        <div class="score-label">Adéquation</div>
                    </div>
                </div>
                <div style='margin: 20px 0;'>
                    {get_score_badge(result['score'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3, gap="medium")
            
            with col1:
                st.markdown("""
                <div class="analysis-section section-strengths">
                    <h4>✅ Points Forts</h4>
                    <ul>
                """, unsafe_allow_html=True)
                for point in result['points_forts']:
                    st.markdown(f'<li><span class="bullet" style="color: #28a745;">●</span> {point}</li>', unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="analysis-section section-improvements">
                    <h4>⚠️ À Améliorer</h4>
                    <ul>
                """, unsafe_allow_html=True)
                for point in result['points_amelioration']:
                    st.markdown(f'<li><span class="bullet" style="color: #ffc107;">●</span> {point}</li>', unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="analysis-section section-recommendations">
                    <h4>💡 Recommandations</h4>
                    <ul>
                """, unsafe_allow_html=True)
                for rec in result['recommandations']:
                    st.markdown(f'<li><span class="bullet" style="color: #17a2b8;">●</span> {rec}</li>', unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
        
        # Export buttons
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            export_data = {
                "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre_candidats": len(st.session_state.results),
                "resultats": st.session_state.results
            }
            st.download_button(
                label="📥 EXPORTER EN JSON",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=f"heck_cv_resultats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            pdf_data = generate_pdf_report(st.session_state.results, st.session_state.get('job_description', ''))
            st.download_button(
                label="📄 EXPORTER EN PDF",
                data=pdf_data,
                file_name=f"heck_cv_rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    main()