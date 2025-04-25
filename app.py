import streamlit as st
from fpdf import FPDF
from PIL import Image
import os
import re

# App-Titel
st.set_page_config(page_title="Monti – Dein PDF-Generator", layout="wide")

# App-Überschrift
st.title("Monti – Dein PDF-Generator")
st.markdown(
    "Willkommen bei **Monti**, deinem KI-Dokumenten-Assistenten. "
    "Gib den Text ein, lade Bilder hoch, und Monti erstellt automatisch ein perfekt formatiertes PDF!"
)

# Eingabe des Textes
text_input = st.text_area("Gib den Text für das PDF ein (Text wird automatisch auf Seiten verteilt)")

# Auswahl für das Layout der Bilder
layout_option = st.selectbox("Wie möchtest du die Bilder anordnen?", [
    "Bild oben, Text unten",
    "Text oben, Bild unten",
    "Bild und Text nebeneinander",
    "Nur Text",
    "Nur Bild"
])

# Bilder hochladen
image_files = st.file_uploader("Lade Bilder hoch", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

# PDF erstellen, wenn der Button geklickt wird
if st.button("PDF generieren"):
    # PDF-Instanz erstellen
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=12)  # Standard-Schriftart und Größe

    # Text auf Seiten verteilen und automatisch Seiten erstellen
    paragraphs = [p.strip() for p in text_input.split("\n") if p.strip()]
    page_limit = 50  # max. Zeilen pro Seite

    for i, paragraph in enumerate(paragraphs):
        if i % page_limit == 0:
            pdf.add_page()

        if paragraph.isupper() or re.match(r"^\d+\.|#|-", paragraph.strip()):
            pdf.set_font("Arial", style='B', size=14)  # Überschrift (fett)
        else:
            pdf.set_font("Arial", size=12)  # Normaler Text

        pdf.multi_cell(0, 10, paragraph, align='L')  # Text hinzufügen

    # Bilder hinzufügen (falls vorhanden)
    if image_files:
        for img_file in image_files:
            pdf.add_page()
            img = Image.open(img_file)
            img_path = f"temp_image.png"
            img.save(img_path)
            pdf.image(img_path, x=10, y=20, w=190)
            os.remove(img_path)

    # PDF-Datei speichern und herunterladen
    pdf_output = "monti_generated_document.pdf"
    pdf.output(pdf_output)

    with open(pdf_output, "rb") as f:
        st.download_button("PDF-Datei herunterladen", f, file_name=pdf_output)

    # Temp-Datei entfernen
    os.remove(pdf_output)
