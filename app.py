import os
from fpdf import FPDF
import streamlit as st
from PIL import Image

# App-Titel
st.set_page_config(page_title="Monti – Dein PDF-Generator", layout="wide")

# App-Überschrift
st.title("Monti – Dein PDF-Generator")
st.markdown(
    "Willkommen bei **Monti**, deinem PDF-Dokumenten-Assistenten. "
    "Du kannst hier Text hinzufügen, Bilder hochladen und daraus ein "
    "strukturiertes PDF erstellen."
)

# Textinput für die PDF
text_input = st.text_area("Gib den Text für dein PDF ein", height=200)

# Auswahl, ob das Bild hinzugefügt werden soll
add_image = st.checkbox("Bild auf der Seite hinzufügen", value=True)

# Bild hochladen, wenn die Option aktiviert ist
image_upload = None
if add_image:
    image_upload = st.file_uploader("Bild hochladen (optional)", type=["png", "jpg", "jpeg"])

# Überprüfen, ob der Text eingegeben wurde
if text_input:
    # Button zum Erstellen der PDF
    if st.button("PDF erstellen"):
        # Verzeichnispfad für die Ausgabe-PDF
        output_dir = "output_files"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Dateipfad für die PDF-Ausgabe
        pdf_output = os.path.join(output_dir, "monti_dokument.pdf")

        # Erstellen der PDF mit FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Text in die PDF einfügen
        paragraphs = [p.strip() for p in text_input.split("\n") if p.strip()]
        for paragraph in paragraphs:
            pdf.multi_cell(0, 10, paragraph, align="L")

        # Bild in die PDF einfügen, falls ein Bild hochgeladen wurde
        if add_image and image_upload:
            img = Image.open(image_upload)
            img_path = "temp_img.png"
            img.save(img_path)
            pdf.add_page()
            pdf.image(img_path, x=10, y=20, w=180)  # Bild positionieren und Größe anpassen
            os.remove(img_path)

        # PDF speichern
        pdf.output(pdf_output, 'F')

        # Download-Link für die generierte PDF bereitstellen
        with open(pdf_output, "rb") as f:
            st.download_button("PDF herunterladen", f, file_name="monti_dokument.pdf")

        st.success("PDF wurde erfolgreich erstellt!")
