import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
from PIL import Image
import re

# App-Titel
st.set_page_config(page_title="Monti – Dein PDF-Generator", layout="wide")

# App-Überschrift
st.title("Monti – Dein PDF-Generator")
st.markdown(
    "Willkommen bei **Monti**, deinem KI-Dokumenten-Assistenten. "
    "Du kannst hier Text eingeben und daraus ein PDF-Dokument erstellen – einfach und schnell."
)

# Auswahl: PDF erstellen
doc_type = st.selectbox("Was möchtest du erstellen?", ["PDF (Text)"])

# PDF-Modus
if doc_type == "PDF (Text)":
    st.subheader("PDF mit Text erstellen")

    # Schriftgrößen für Text und Überschrift wählen
    text_size = st.slider("Wähle die Schriftgröße für den Text (10-12 pt)", 10, 12, 11)
    heading_size = st.slider("Wähle die Schriftgröße für Überschriften (13-15 pt)", 13, 15, 14)

    # Seitenanzahl und Seitenzahlen
    total_pages = st.slider("Wie viele Seiten soll dein PDF haben? (1-1000)", 1, 1000, 2)
    show_page_numbers = st.checkbox("Seitenzahlen auf allen Seiten anzeigen", value=False)

    seiten_content = []
    for i in range(total_pages):
        st.markdown(f"### Seite {i+1}")
        text = st.text_area(f"Text für Seite {i+1}", key=f"text_{i}")

        seiten_content.append(text)

    if st.button("PDF generieren"):
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=10)

        # Standard-Schriftart (keine benutzerdefinierte Schriftart erforderlich)
        pdf.set_font("Arial", size=text_size)

        for idx, text in enumerate(seiten_content):
            pdf.add_page()
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
            for paragraph in paragraphs:
                if paragraph.isupper() or re.match(r"^\d+\.|#|-", paragraph.strip()):
                    pdf.set_font("Arial", style='B', size=heading_size)  # Fettdruck für Überschriften
                else:
                    pdf.set_font("Arial", size=text_size)
                pdf.multi_cell(0, 10, paragraph, align='L')

        pdf_file = "monti_text_dokument.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button("PDF-Datei herunterladen", f, file_name=pdf_file)
        os.remove(pdf_file)
