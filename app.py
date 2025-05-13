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
import os

# Fonts registrieren
pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('NotoSans', 'fonts/NotoSans-Regular.ttf'))

st.set_page_config(page_title="Monti - Dokumenten-Bot", layout="wide")

# Stil
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

# Layout: Zwei Spalten
col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://i.postimg.cc/wMp2sCF4/Design-ohne-Titel-9.png", width=280)

with col2:
    st.markdown("<div class='title'><h1>📄 Monti – Dein intelligenter PDF-Generator</h1></div>", unsafe_allow_html=True)

    # Auswahl des Dokumententyps
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

    def generate_ebook(text, images):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        for line in text.split("\n"):
            if line.strip().startswith("#"):
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(line.strip('# ').strip(), title_style))
            else:
                elements.append(Paragraph(line.strip(), custom_style))
                elements.append(Spacer(1, 6))

        if images:
            for img in images:
                elements.append(Spacer(1, 12))
                elements.append(RLImage(img, width=12*cm, height=8*cm))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def generate_invoice():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        if logo_file:
            elements.append(RLImage(logo_file, width=4*cm, height=2*cm))
            elements.append(Spacer(1, 8))

        elements.append(Paragraph("Rechnung", title_style))
        elements.append(Spacer(1, 12))

        data = [
            ["Beschreibung", "Menge", "Einzelpreis", "Gesamt"],
            ["Produkt A", "2", "100 €", "200 €"],
            ["Produkt B", "1", "150 €", "150 €"],
            ["", "", "<b>Gesamt</b>", "<b>350 €</b>"]
        ]
        table = Table(data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), color_map[design_choice]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), font_choice)
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return buffer

    text_input = st.text_area("Dein Text (mit # für Kapitelüberschriften)", height=300)
    image_files = []
    if option == "E-Book":
        image_files = st.file_uploader("Bilder hochladen (optional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if st.button("📥 PDF erstellen"):
        if option == "E-Book":
            if not text_input:
                st.warning("Bitte Text eingeben.")
            else:
                pdf_buffer = generate_ebook(text_input, image_files)
                st.download_button("📘 E-Book herunterladen", data=pdf_buffer, file_name="ebook.pdf", mime="application/pdf")

                # Vorschau in Spalte 2 anzeigen
                with st.expander("📄 Vorschau anzeigen"):
                    base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)

        elif option == "Rechnung":
            pdf_buffer = generate_invoice()
            st.download_button("🧾 Rechnung herunterladen", data=pdf_buffer, file_name="rechnung.pdf", mime="application/pdf")

            with st.expander("📄 Vorschau anzeigen"):
                base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

        else:
            st.info("Dieses Dokumentenformat wird bald unterstützt.")
