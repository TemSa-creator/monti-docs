import streamlit as st
from fpdf import FPDF
from PIL import Image
import os
import io
import re
from pdf2image import convert_from_path

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

# PDF generieren, wenn der Button geklickt wird
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

    # PDF-Datei speichern in einem io.BytesIO-Objekt, um es im Streamlit anzuzeigen
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)  # Zurück zum Anfang der Datei gehen

    # PDF in Bild umwandeln
    images = convert_from_path(pdf_output)
    image_preview = images[0]  # Die erste Seite als Vorschau
    preview_path = "preview_image.png"
    image_preview.save(preview_path)

    # PDF-Vorschau anzeigen
    st.sidebar.markdown("### Vorschau der PDF-Datei:")
    st.sidebar.image(preview_path, caption="Vorschau der PDF", use_column_width=True)

    # PDF-Datei herunterladen
    st.sidebar.download_button("Download PDF", pdf_output, file_name="monti_generated_document.pdf")

    # Temp-Datei entfernen
    os.remove(preview_path)
