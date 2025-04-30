import io
from fpdf import FPDF
import streamlit as st
from streamlit_quill import st_quill

# Funktion zur Erstellung der PDF mit Text und Bild
def create_pdf(text, image_path=None):
    pdf = FPDF()
    pdf.add_page()

    # Setze die Schriftart
    pdf.set_font("Arial", size=12)

    # Füge den Text ein
    pdf.multi_cell(0, 10, text)

    # Füge das Bild ein, falls vorhanden
    if image_path:
        pdf.image(image_path, x=10, y=50, w=100)  # Bild einfügen an der Position (10, 50) mit Breite 100mm

    return pdf

# Layout der Streamlit-App
st.title("Monti - Dein PDF-Generator")

# Quill Editor für die Texterstellung
text_input = st_quill(placeholder="Gib den Text für dein PDF ein", height=300)

# Checkbox für das Hinzufügen eines Bildes
add_image = st.checkbox("Bild auf der Seite hinzufügen")

# Bild hochladen (nur wenn die Checkbox aktiviert ist)
image = None
if add_image:
    image = st.file_uploader("Lade ein Bild hoch", type=["jpg", "png", "jpeg"])

# PDF-Erstellung und Download
if st.button("PDF erstellen"):
    # Den Text aus dem Quill Editor holen
    if text_input:
        raw_text = text_input['text']  # Der Quill Editor gibt ein Dictionary zurück

        # PDF erstellen
        pdf = create_pdf(raw_text, image)

        # PDF in BytesIO speichern (anstatt auf der Festplatte)
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)  # Den Cursor zurück auf den Anfang setzen

        # PDF zum Download anbieten
        st.download_button(
            label="PDF herunterladen",
            data=pdf_output,
            file_name="dein_pdf.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Bitte gib Text ein, um das PDF zu erstellen!")
