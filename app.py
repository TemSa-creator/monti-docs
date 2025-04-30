import io
from fpdf import FPDF
import streamlit as st
from streamlit_quill import st_quill

# Funktion zur Erstellung der PDF
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    return pdf

# Layout der Streamlit-App
st.title("Monti - Dein PDF-Generator")

# Quill Editor für die Texterstellung
text_input = st_quill(placeholder="Gib den Text für dein PDF ein", height=300)

# Checkbox für das Hinzufügen eines Bildes
add_image = st.checkbox("Bild auf der Seite hinzufügen")

# PDF-Erstellung und Download
if st.button("PDF erstellen"):
    # Den Text aus dem Quill Editor holen
    raw_text = text_input['text']  # Der Quill Editor gibt ein Dictionary zurück
    
    # PDF erstellen
    pdf = create_pdf(raw_text)
    
    # Wenn ein Bild hinzugefügt werden soll, dann ein Bild im PDF einfügen
    if add_image:
        # Hier wird ein Beispielbild hinzugefügt. Achte darauf, dass der Pfad korrekt ist.
        # Du kannst auch den Upload von Bildern integrieren, falls du ein Bild vom Benutzer erhalten möchtest
        pdf.image("dein_bild.jpg", x = 10, y = 50, w = 100)  # Beispielbild-URL
    
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
