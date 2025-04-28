import os
import streamlit as st
from fpdf import FPDF
from PIL import Image
from streamlit_quill import st_quill

# App-Titel
st.set_page_config(page_title="Monti – Dein PDF-Generator", layout="wide")

# App-Überschrift
st.title("Monti – Dein PDF-Generator")
st.markdown(
    "Willkommen bei **Monti**, deinem PDF-Dokumenten-Assistenten. "
    "Du kannst hier Text hinzufügen, Bilder hochladen und daraus ein "
    "strukturiertes PDF erstellen."
)

# Rich Text Editor (Quill)
st.markdown("### Gib hier deinen Text ein und formatiere ihn nach Belieben")
quill_text = st_quill(key="quill_editor")

# Auswahl, ob das Bild hinzugefügt werden soll
add_image = st.checkbox("Bild auf der Seite hinzufügen", value=True)

# Bild hochladen, wenn die Option aktiviert ist
image_upload = None
if add_image:
    image_upload = st.file_uploader("Bild hochladen (optional)", type=["png", "jpg", "jpeg"])

# Überprüfen, ob der Text eingegeben wurde
if quill_text:
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

        # Versuchen, die Schriftart hinzuzufügen
        try:
            # DejaVu Sans oder Noto Sans als Schriftart laden
            pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
            pdf.set_font('DejaVu', size=12)
        except Exception as e:
            st.error(f"Fehler beim Laden der Schriftart: {str(e)}")
            st.stop()

        # Text in die PDF einfügen
        paragraphs = [p.strip() for p in quill_text.split("\n") if p.strip()]
        for paragraph in paragraphs:
            # Einfacher HTML-Parser (nur für grundlegende Tags wie <b>, <i> und <font>)
            paragraph = paragraph.replace("<b>", "").replace("</b>", "")  # Fett
            paragraph = paragraph.replace("<i>", "").replace("</i>", "")  # Kursiv
            paragraph = paragraph.replace("<u>", "").replace("</u>", "")  # Unterstrichen

            # Hier kannst du das Format noch erweitern

            # Füge den Text hinzu, formatiere ihn entsprechend
            pdf.multi_cell(0, 10, paragraph, align="L")

        # Bild in die PDF einfügen, falls ein Bild hochgeladen wurde
        if add_image and image_upload:
            img = Image.open(image_upload)
            img_path = "temp_img.png"
            img.save(img_path)
            
            # Bildgröße anpassen (maximal 100mm breite)
            img_width = 100  # Maximale Breite des Bildes
            img_height = (img.height * img_width) / img.width  # Höhe proportional anpassen
            
            # Bild positionieren und Größe anpassen
            pdf.image(img_path, x=10, y=pdf.get_y() + 5, w=img_width, h=img_height)
            os.remove(img_path)  # Temporäre Bilddatei löschen

        # PDF speichern
        pdf.output(pdf_output, 'F')

        # Download-Link für die generierte PDF bereitstellen
        with open(pdf_output, "rb") as f:
            st.download_button("PDF herunterladen", f, file_name="monti_dokument.pdf")

        st.success("PDF wurde erfolgreich erstellt!")
