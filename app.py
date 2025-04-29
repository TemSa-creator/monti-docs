from fpdf import FPDF
import streamlit as st
from streamlit_quill import st_quill

# Quill Textfeld für die PDF
text_input = st_quill(placeholder="Gib den Text für dein PDF ein", height=300)

# Auswahl, ob das Bild hinzugefügt werden soll
add_image = st.checkbox("Bild auf der Seite hinzufügen", value=True)

# PDF-Generierung
if text_input:
    pdf = FPDF()
    pdf.add_page()

    # Schriftart, die Sonderzeichen unterstützt
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)  # Stelle sicher, dass 'arial.ttf' im richtigen Verzeichnis ist
    pdf.set_font('Arial', size=12)

    # Text aus Quill Editor
    text = text_input['text']  # Quill gibt den Text als HTML zurück, daher 'text' verwenden

    # Text zum PDF hinzufügen
    pdf.multi_cell(0, 10, text)

    # Bild hinzufügen, falls ausgewählt
    if add_image:
        image_path = st.file_uploader("Lade ein Bild hoch", type=["jpg", "png"])
        if image_path:
            pdf.image(image_path, x=10, y=pdf.get_y(), w=100)

    # PDF speichern
    pdf_output = "/mnt/data/generated_pdf.pdf"
    pdf.output(pdf_output, 'F')

    st.download_button("Download PDF", pdf_output)
