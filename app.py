import re
from fpdf import FPDF
import streamlit as st
from streamlit_quill import st_quill

# Funktion, um HTML-Tags zu entfernen und Textformatierungen zu verarbeiten
def process_text(text):
    # Entfernen von HTML-Tags
    text = re.sub(r'<.*?>', '', text)
    # Ersetzen von HTML für fett und kursiv mit passenden FPDF-Steuerzeichen
    text = text.replace('<b>', '').replace('</b>', '*')  # Fett wird durch * ersetzt
    text = text.replace('<i>', '').replace('</i>', '_')  # Kursiv wird durch _ ersetzt
    return text

# Quill Textfeld für die PDF
text_input = st_quill(placeholder="Gib den Text für dein PDF ein", height=300)

# Auswahl, ob das Bild hinzugefügt werden soll
add_image = st.checkbox("Bild auf der Seite hinzufügen", value=True)

# PDF-Generierung
if text_input:
    pdf = FPDF()
    pdf.add_page()

    # Schriftart, die Sonderzeichen unterstützt
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)  # Stelle sicher, dass die Schriftart lokal verfügbar ist
    pdf.set_font('DejaVu', '', 12)

    # Text aus Quill Editor verarbeiten
    raw_text = text_input['text']
    processed_text = process_text(raw_text)

    # Text zum PDF hinzufügen
    pdf.multi_cell(0, 10, processed_text)

    # Bild hinzufügen, falls ausgewählt
    if add_image:
        image_path = st.file_uploader("Lade ein Bild hoch", type=["jpg", "png"])
        if image_path:
            pdf.image(image_path, x=10, y=pdf.get_y(), w=100)

    # PDF speichern
    pdf_output = "/mnt/data/generated_pdf.pdf"
    pdf.output(pdf_output, 'F')

    st.download_button("Download PDF", pdf_output)
