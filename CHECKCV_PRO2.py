"""
CHECK CV - Version Production
Supporte jusqu'à 100 CV, Export PDF structuré selon le modèle officiel.
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from mistralai.client import MistralClient
import json
from typing import List, Dict, Any
import io
from datetime import datetime

# Import pour la génération PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="CHECK CV - Analyseur Multi-Candidats",
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

    .analysis-section {
        border-radius: 16px; padding: 20px; margin-top: 15px;
        height: 100%; color: #ffffff !important;
    }
    .section-strengths { background-color: #1a73e8; } 
    .section-improvements { background-color: #f9ab00; }
    .section-recommendations { background-color: #34a853; }

    .analysis-section h4 { color: #ffffff !important; text-transform: uppercase; font-size: 0.9em; letter-spacing: 1px; margin-bottom: 15px; }
    .analysis-section p, .analysis-section li, .analysis-section div { color: #ffffff !important; font-size: 0.95em; line-height: 1.5; }

    .stButton > button {
        background-color: #0b57d0 !important; color: white !important;
        border-radius: 100px !important; padding: 12px 30px !important;
        width: 100%; border: none !important; font-weight: 500;
    }
    .export-container { display: flex; gap: 10px; justify-content: center; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE MISTRAL ---

@st.cache_resource
def init_mistral():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        st.error("Clé API Mistral manquante.")
        st.stop()
    return MistralClient(api_key=api_key)

def extract_text(file) -> str:
    try:
        if file.type == "application/pdf":
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import docx
            doc = docx.Document(io.BytesIO(file.getvalue()))
            return "\n".join([p.text for p in doc.paragraphs])
        return file.getvalue().decode("utf-8")
    except Exception:
        return ""

def analyze_cv(client, job_txt, cv_txt, name):
    # Prompt optimisé pour la stabilité du JSON avec plusieurs CV
    prompt = f"""Tu es un expert RH. Analyse ce CV par rapport à l'offre d'emploi.
    Réponds EXCLUSIVEMENT en JSON valide.
    Format : {{
      "nom_complet": "Nom du candidat",
      "score": 85,
      "points_forts": ["point 1", "point 2"],
      "points_amelioration": ["point 1", "point 2"],
      "recommandations": ["point 1", "point 2"]
    }}
    Offre : {job_txt[:2000]}
    CV ({name}) : {cv_txt[:4000]}"""
    
    try:
        from mistralai.models.chat_completion import ChatMessage
        resp = client.chat(model="mistral-large-latest", messages=[ChatMessage(role="user", content=prompt)], temperature=0.2)
        content = resp.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
        return json.loads(content)
    except:
        return None

# --- GÉNÉRATION DU RAPPORT PDF (MODÈLE OFFICIEL) ---

def generate_pdf_report(results):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontSize=18)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], color=colors.black, spaceAfter=10, fontSize=14)
    header_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ])

    elements = []
    
    # En-tête du rapport
    elements.append(Paragraph("CHECK CV - RAPPORT D'ANALYSE", title_style))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # RÉSUMÉ DE L'ANALYSE (Tableau de stats)
    elements.append(Paragraph("RÉSUMÉ DE L'ANALYSE", styles['Heading2']))
    
    total = len(results)
    excellent = len([r for r in results if r.get('score', 0) >= 80])
    bon = len([r for r in results if 60 <= r.get('score', 0) < 80])
    moyen = len([r for r in results if 40 <= r.get('score', 0) < 60])
    faible = len([r for r in results if r.get('score', 0) < 40])

    summary_data = [
        ["Nombre de candidats analysés:", str(total)],
        ["Excellent (80%+):", str(excellent)],
        ["Bon (60-79%):", str(bon)],
        ["Moyen (40-59%):", str(moyen)],
        ["Faible (<40%):", str(faible)]
    ]
    
    summary_table = Table(summary_data, colWidths=[250, 100])
    summary_table.setStyle(header_table_style)
    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # DÉTAILS PAR CANDIDAT
    for i, r in enumerate(results):
        elements.append(Paragraph(f"CANDIDAT #{i+1}", styles['Heading2']))
        elements.append(Paragraph(f"<b>Nom:</b> {r.get('nom_complet', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fichier:</b> {r.get('filename', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Score d'adéquation:</b> {r.get('score', 0)}%", styles['Normal']))
        elements.append(Spacer(1, 10))

        # Sections Points Forts, Faibles, Recommandations
        sections = [
            ("POINTS FORTS", r.get('points_forts', [])),
            ("POINTS À AMÉLIORER", r.get('points_amelioration', [])),
            ("RECOMMANDATIONS", r.get('recommandations', []))
        ]

        for sec_title, sec_items in sections:
            elements.append(Paragraph(f"<b>{sec_title}</b>", styles['Normal']))
            for item in sec_items:
                elements.append(Paragraph(f"• {item}", ParagraphStyle('Bullet', parent=styles['Normal'], leftIndent=20, spaceBefore=2)))
            elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 20))
        if (i + 1) % 2 == 0: # Saut de page tous les 2 candidats pour aérer
            elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer

def format_item(item: Any) -> str:
    if isinstance(item, str): return item
    if isinstance(item, dict): return item.get('details', item.get('action', str(item)))
    return str(item)

# --- APPLICATION ---

def main():
    st.markdown('<div class="professional-header"><h1>CHECK CV</h1><p>Analyse de Masse & Pipeline RAG (jusqu\'à 100 CV)</p></div>', unsafe_allow_html=True)
    client = init_mistral()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="upload-card"><h3>📄 Offre d\'emploi</h3>', unsafe_allow_html=True)
        job_f = st.file_uploader("Upload Job", type=["pdf", "txt", "docx"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="upload-card"><h3>👥 CV Candidats (Max 100)</h3>', unsafe_allow_html=True)
        cv_fs = st.file_uploader("Upload CVs", type=["pdf", "txt", "docx"], accept_multiple_files=True, label_visibility="collapsed")
        if cv_fs and len(cv_fs) > 100:
            st.warning("⚠️ Limite de 100 CV dépassée. Seuls les 100 premiers seront analysés.")
            cv_fs = cv_fs[:100]
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 LANCER L'ANALYSE") and job_f and cv_fs:
        job_text = extract_text(job_f)
        results = []
        bar = st.progress(0)
        status = st.empty()
        
        for i, f in enumerate(cv_fs):
            status.info(f"Analyse du candidat {i+1}/{len(cv_fs)} : {f.name}")
            res = analyze_cv(client, job_text, extract_text(f), f.name)
            if res:
                res['filename'] = f.name
                results.append(res)
            bar.progress((i + 1) / len(cv_fs))
        
        status.success(f"Analyse terminée ! {len(results)} candidats traités.")
        st.session_state['results'] = sorted(results, key=lambda x: x['score'], reverse=True)
        st.rerun()

    if 'results' in st.session_state:
        res_list = st.session_state['results']
        
        # ZONE D'EXPORT (Boutons PDF et JSON)
        st.markdown('<div class="export-container">', unsafe_allow_html=True)
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            pdf_report = generate_pdf_report(res_list)
            st.download_button("📥 Télécharger Rapport PDF (Modèle Officiel)", data=pdf_report, file_name=f"check_cv_rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf")
        with col_ex2:
            json_str = json.dumps(res_list, indent=2, ensure_ascii=False)
            st.download_button("📦 Exporter Données JSON", data=json_str, file_name="Analyse_Candidats.json", mime="application/json")
        st.markdown('</div>', unsafe_allow_html=True)

        # AFFICHAGE DES CARTES CANDIDATS
        for r in res_list:
            st.markdown(f"""
            <div class="result-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div><h2 style="margin:0; color:#1f1f1f;">{r['nom_complet']}</h2><small style="color:#666;">Fichier : {r['filename']}</small></div>
                    <div style="text-align:right"><div class="score-number">{r['score']}%</div><b>SCORE</b></div>
                </div>
            </div>""", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            sections = [
                (c1, "points_forts", "section-strengths", "✅ Points Forts"),
                (c2, "points_amelioration", "section-improvements", "⚠️ À Améliorer"),
                (c3, "recommandations", "section-recommendations", "💡 Conseils")
            ]

            for col, key, css, title in sections:
                with col:
                    st.markdown(f'<div class="analysis-section {css}"><h4>{title}</h4>', unsafe_allow_html=True)
                    for item in r.get(key, []):
                        st.write(f"• {format_item(item)}")
                    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
