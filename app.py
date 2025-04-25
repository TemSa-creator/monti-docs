import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
from PIL import Image
import re

# App-Titel
st.set_page_config(page_title="Monti – Dein PDF- & Excel-Generator", layout="wide")

# App-Überschrift
st.title("Monti – Dein PDF- & Excel-Generator")
st.markdown(
    "Willkommen bei **Monti**, deinem KI-Dokumenten-Assistenten. "
    "Du kannst hier Excel-Tabellen erstellen, Bilder hochladen und daraus ein "
    "strukturiertes PDF machen – z. B. für Kinderbücher, Berichte oder kreative Projekte."
)

# Auswahl: Excel oder PDF
doc_type = st.selectbox("Was möchtest du erstellen?", ["PDF (Text + Bilder)", "Excel-Tabelle"])

# Excel-Modus
if doc_type == "Excel-Tabelle":
    st.subheader("Excel-Tabelle erstellen")
    columns_input = st.text_input("Gib die Spaltennamen ein (durch Komma getrennt)", "Datum,Betrag,Kategorie")
    columns = [col.strip() for col in columns_input.split(",")]

    data = []
    st.markdown("### Daten eingeben")
    for i in range(5):
        row = []
        cols = st.columns(len(columns))
        for j, col_name in enumerate(columns):
            value = cols[j].text_input(f"{col_name} (Zeile {i+1})", key=f"{i}-{j}")
            row.append(value)
        data.append(row)

    if st.button("Excel generieren"):
        df = pd.DataFrame(data, columns=columns)
        file_name = "monti_excel_tabelle.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button("Excel-Datei herunterladen", f, file_name=file_name)
        os.remove(file_name)

# PDF-Modus
if doc_type == "PDF (Text + Bilder)":
    st.subheader("PDF mit Bildern und Text erstellen")

    format_option = st.selectbox("Wähle dein Buchformat (KDP-kompatibel):", ["6 x 9 Zoll", "7 x 10 Zoll", "8.25 x 11 Zoll", "A5"])
    format_mapping = {
        "6 x 9 Zoll": (152, 229),
        "7 x 10 Zoll": (178, 254),
        "8.25 x 11 Zoll": (210, 280),
        "A5": (148, 210)
    }
    page_w, page_h = format_mapping[format_option]

    # Schriftgrößen für Text und Überschrift wählen
    text_size = st.slider("Wähle die Schriftgröße für den Text (10-12 pt)", 10, 12, 11)
    heading_size = st.slider("Wähle die Schriftgröße für Überschriften (13-15 pt)", 13, 15, 14)

    # Seitenanzahl und Seitenzahlen
    total_pages = st.slider("Wie viele Seiten soll dein PDF haben? (1-1000)", 1, 1000, 2)
    show_page_numbers = st.checkbox("Seitenzahlen auf allen Seiten anzeigen", value=False)

    vorlage = st.selectbox("Vorlage wählen (optional)", [
        "Freies Projekt",
        "Kinderbuch (10 Seiten)",
        "Malbuch (12 Seiten)",
        "Workbook (7 Seiten)",
        "Mini-Ratgeber (5 Kapitel)",
        "Notizbuch (100 leere Seiten)",
        "Mehrere Bilder automatisch anordnen"
    ])

    if vorlage == "Kinderbuch (10 Seiten)":
        seiten = 10
    elif vorlage == "Malbuch (12 Seiten)":
        seiten = 12
    elif vorlage == "Workbook (7 Seiten)":
        seiten = 7
    elif vorlage == "Mini-Ratgeber (5 Kapitel)":
        seiten = 5
    elif vorlage == "Notizbuch (100 leere Seiten)":
        seiten = 100
    elif vorlage == "Mehrere Bilder automatisch anordnen":
        bilder_upload = st.file_uploader("Mehrere Bilder hochladen", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        if bilder_upload and st.button("PDF aus Bildern erstellen"):
            pdf = FPDF(orientation="P", unit="mm", format=(page_w, page_h))
            pdf.set_auto_page_break(auto=True, margin=10)
            try:
                # Hier die Schriftart einfügen
                pdf.add_font('Noto', '', 'NotoSans-Regular.ttf', uni=True)
                pdf.set_font('Noto', '', heading_size)
            except:
                st.error("Schriftart konnte nicht geladen werden. Bitte überprüfe den Font-Pfad!")
                st.stop()
                
            for idx, img_file in enumerate(bilder_upload):
                pdf.add_page()
                img = Image.open(img_file)
                img_path = f"temp_multi_img_{idx}.png"
                img.save(img_path)
                pdf.image(img_path, x=10, y=20, w=page_w - 20)
                os.remove(img_path)
            pdf_file = "monti_bilderbuch.pdf"
            pdf.output(pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button("PDF-Datei herunterladen", f, file_name=pdf_file)
            st.success("PDF mit Bildern erfolgreich erstellt!")
            st.stop()
        seiten = 0
    else:
        seiten = total_pages

    if seiten > 0:
        logo_file = st.file_uploader("Optional: Logo hochladen (wird oben rechts eingefügt)", type=["png", "jpg", "jpeg"])
        use_logo = st.checkbox("Logo auf allen Seiten anzeigen", value=False)

        impressum_text = st.text_area("Optional: Impressumstext eingeben")
        impressum_position = st.selectbox("Wo soll das Impressum erscheinen?", ["Am Anfang (Seite 1)", "Am Ende (letzte Seite)", "Benutzerdefinierte Seite"])
        benutzerdefiniert = None
        if impressum_position == "Benutzerdefinierte Seite":
            benutzerdefiniert = st.number_input("Auf welcher Seite soll das Impressum stehen?", min_value=1, max_value=seiten, value=seiten)

        seiten_content = []
        for i in range(seiten):
            st.markdown(f"### Seite {i+1}")
            text = st.text_area(f"Text für Seite {i+1}", key=f"text_{i}")
            image = st.file_uploader(f"Bild für Seite {i+1} hochladen", type=["png", "jpg", "jpeg"], key=f"img_{i}")
            layout_style = st.selectbox(f"Layout-Stil für Seite {i+1}", [
                "Bild oben, Text unten", "Text oben, Bild unten",
                "Text neben Bild", "Nur Text", "Nur Bild"
            ], key=f"layout_{i}")
            seiten_content.append((text, image, layout_style))

        if st.button("PDF generieren"):
            pdf = FPDF(orientation="P", unit="mm", format=(page_w, page_h))
            pdf.set_auto_page_break(auto=True, margin=10)
            try:
                pdf.add_font('Noto', '', 'NotoSans-Regular.ttf', uni=True)
                pdf.set_font('Noto', '', text_size)
            except:
                st.error("Schriftart konnte nicht geladen werden. Bitte überprüfe den Font-Pfad!")
                st.stop()

            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                logo_path = "temp_logo.png"
                logo_img.save(logo_path)

            for idx, (text, img_file, layout) in enumerate(seiten_content):
                pdf.add_page()
                if use_logo and logo_path:
                    pdf.image(logo_path, x=page_w - 40, y=10, w=30)

                if layout == "Nur Text" or layout == "Text oben, Bild unten" or layout == "Text neben Bild":
                    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
                    for paragraph in paragraphs:
                        if paragraph.isupper() or re.match(r"^\d+\.|#|-", paragraph.strip()):
                            pdf.set_font("Noto", style='B', size=heading_size)
                        else:
                            pdf.set_font("Noto", size=text_size)
                        pdf.multi_cell(0, 10, paragraph, align='C')

                if layout == "Nur Bild" and img_file:
                    img = Image.open(img_file)
                    img_path = f"temp_img_{idx}.png"
                    img.save(img_path)
                    pdf.image(img_path, x=10, y=20, w=page_w - 20)
                    os.remove(img_path)

                if layout == "Bild oben, Text unten":
                    if img_file:
                        img = Image.open(img_file)
                        img_path = f"temp_img_{idx}.png"
                        img.save(img_path)
                        pdf.image(img_path, x=10, y=20, w=page_w - 20)
                        os.remove(img_path)
                        pdf.set_y(130)
                    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
                    for paragraph in paragraphs:
                        if paragraph.isupper() or re.match(r"^\d+\.|#|-", paragraph.strip()):
                            pdf.set_font("Noto", style='B', size=heading_size)
                        else:
                            pdf.set_font("Noto", size=text_size)
                        pdf.multi_cell(0, 10, paragraph, align='C')

                if impressum_text:
                    if (impressum_position == "Am Anfang (Seite 1)" and idx == 0) or \
                       (impressum_position == "Am Ende (letzte Seite)" and idx == seiten - 1) or \
                       (impressum_position == "Benutzerdefinierte Seite" and idx == benutzerdefiniert - 1):
                        pdf.ln(10)
                        pdf.set_font("Noto", style='I', size=9)
                        pdf.multi_cell(0, 8, f"Impressum: {impressum_text}", align='C')

            pdf_file = "monti_dokument.pdf"
            pdf.output(pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button("PDF-Datei herunterladen", f, file_name=pdf_file)
            os.remove(pdf_file)
            if logo_path:
                os.remove(logo_path)
