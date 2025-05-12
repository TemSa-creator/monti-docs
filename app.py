import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
import io

st.set_page_config(page_title="Monti - Dokumenten-Bot", layout="centered")
st.title("📄 Monti – Dein intelligenter PDF-Generator")

# Auswahl des Dokumententyps
option = st.selectbox("Was möchtest du erstellen?", [
    "E-Book",
    "Rechnung",
    "Brief",
    "Urkunde",
    "Präsentation",
])

styles = getSampleStyleSheet()
custom_style = ParagraphStyle(
    name='Custom',
    parent=styles['Normal'],
    fontSize=12,
    leading=16
)

def generate_ebook(text, images):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    for line in text.split("\n"):
        if line.strip().startswith("#"):
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"<b>{line.strip('# ').strip()}</b>", styles['Heading2']))
        else:
            elements.append(Paragraph(line.strip(), custom_style))
            elements.append(Spacer(1, 6))

    if images:
        for img in images:
            elements.append(Spacer(1, 12))
            elements.append(Image(img, width=12*cm, height=8*cm))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_invoice():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    elements.append(Paragraph("<b>Rechnung</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [
        ["Beschreibung", "Menge", "Einzelpreis", "Gesamt"],
        ["Produkt A", "2", "100 €", "200 €"],
        ["Produkt B", "1", "150 €", "150 €"],
        ["", "", "<b>Gesamt</b>", "<b>350 €</b>"]
    ]
    table = Table(data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
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

    elif option == "Rechnung":
        pdf_buffer = generate_invoice()
        st.download_button("🧾 Rechnung herunterladen", data=pdf_buffer, file_name="rechnung.pdf", mime="application/pdf")

    else:
        st.info("Dieses Dokumentenformat wird bald unterstützt.")
