import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
from PyPDF2 import PdfReader
import base64
from PIL import Image
import tempfile
import os

# Fonts registrieren
pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('NotoSans', 'fonts/NotoSans-Regular.ttf'))

st.set_page_config(page_title="Monti - Dokumenten-Bot", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
        }
        .title h1 {
            color: gold;
            font-size: 36px;
        }
        .text-area textarea {
            color: black;
            background-color: white;
            border: 1px solid black;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://i.postimg.cc/9Q4sX3M5/Kein-Titel-Lesezeichen.png", width=280)

with col2:
    st.markdown("<div class='title'><h1>📄 Monti – Dein intelligenter PDF-Generator</h1></div>", unsafe_allow_html=True)

    option = st.selectbox("Was möchtest du erstellen?", ["E-Book", "Rechnung", "Brief", "Urkunde", "Präsentation"])

    font_size = st.slider("Schriftgröße", 8, 24, 12)
    line_spacing = st.slider("Zeilenabstand", 10, 30, 16)
    alignment = st.selectbox("Ausrichtung", ["Links", "Zentriert", "Rechts"])
    font_choice = st.selectbox("Schriftart", ["DejaVuSans", "NotoSans"])
    design_choice = st.selectbox("Design-Vorlage", ["Business", "Kreativ", "Minimalistisch"])

    logo_file = st.file_uploader("Firmenlogo hochladen (optional)", type=["jpg", "jpeg", "png"])

    align_map = {"Links": 0, "Zentriert": 1, "Rechts": 2}
    color_map = {
        "Business": colors.HexColor("#2E4053"),
        "Kreativ": colors.HexColor("#8E44AD"),
        "Minimalistisch": colors.black
    }

    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName=font_choice,
        fontSize=font_size + 4,
        leading=line_spacing + 2,
        alignment=align_map[alignment],
        textColor=color_map[design_choice]
    )

    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        name='Custom',
        parent=styles['Normal'],
        fontName=font_choice,
        fontSize=font_size,
        leading=line_spacing,
        alignment=align_map[alignment]
    )

    def convert_uploaded_image(uploaded_file):
        try:
            image = Image.open(uploaded_file).convert("RGB")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                image.save(tmp_file.name, format='JPEG')
                return tmp_file.name
        except Exception as e:
            st.error(f"Bildverarbeitung fehlgeschlagen: {e}")
            return None

    def generate_ebook(text, chapter_image_map):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        lines = text.split("\n")
        current_chapter = None

        for line in lines:
            if line.strip().startswith("#"):
                current_chapter = line.strip('# ').strip().lower()
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(current_chapter.title(), title_style))

                for key, content in chapter_image_map.items():
                    if key.lower() in current_chapter or current_chapter in key.lower():
                        img_path = convert_uploaded_image(content['file'])
                        if img_path and os.path.exists(img_path):
                            try:
                                img = RLImage(img_path, width=12*cm, height=8*cm)
                                pos = content['position']
                                if pos == "Unter Text":
                                    elements.append(Spacer(1, 12))
                                    elements.append(img)
                                elif pos == "Über Text":
                                    elements.insert(-1, img)
                                elif pos == "Neben Text":
                                    table = Table([[img, Paragraph(current_chapter.title(), title_style)]])
                                    elements[-1] = table
                                elif pos == "Hinter Text":
                                    elements.append(Paragraph("[Bild hinter Text – aktuell nicht unterstützt]", custom_style))
                            except Exception as e:
                                elements.append(Paragraph(f"Fehler beim Einfügen des Bildes: {e}", custom_style))
                        else:
                            elements.append(Paragraph("⚠️ Bild konnte nicht geladen werden.", custom_style))
                        break
            else:
                elements.append(Paragraph(line.strip(), custom_style))
                elements.append(Spacer(1, 6))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    text_input = st.text_area("Dein Text (mit # für Kapitelüberschriften)", height=300)
    chapter_image_map = {}

    if option == "E-Book":
        image_files = st.file_uploader("Bilder hochladen", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if image_files:
            for i, img in enumerate(image_files):
                chapter = st.text_input(f"Zu welchem Kapitel gehört dieses Bild? ({img.name})", key=f"ch_{i}")
                position = st.selectbox("Bildposition", ["Unter Text", "Über Text", "Neben Text", "Hinter Text"], key=f"pos_{i}")
                if chapter:
                    chapter_image_map[chapter.lower()] = {"file": img, "position": position}

    if st.button("📄 PDF erstellen"):
        if not text_input:
            st.warning("Bitte Text eingeben.")
        else:
            pdf_buffer = generate_ebook(text_input, chapter_image_map)
            st.download_button("📘 E-Book herunterladen", data=pdf_buffer, file_name="ebook.pdf", mime="application/pdf")
            with st.expander("📄 Vorschau anzeigen"):
                base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
