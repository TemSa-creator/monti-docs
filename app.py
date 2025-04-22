import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
from PIL import Image
from io import BytesIO

# App-Titel
st.set_page_config(page_title="Monti – Dein PDF- & Excel-Generator", layout="centered")
st.title("📘 Monti – Dein PDF- & Excel-Generator")

st.markdown("Willkommen bei **Monti**, deinem KI-Dokumenten-Assistenten. Du kannst hier Excel-Tabellen erstellen, Bilder hochladen und daraus ein strukturiertes PDF machen – z. B. für Kinderbücher, Berichte oder kreative Projekte.")

# Auswahl: Excel oder PDF
doc_type = st.selectbox("Was möchtest du erstellen?", ["PDF (Text + Bilder)", "Excel-Tabelle"])

# Excel-Modus
if doc_type == "Excel-Tabelle":
    st.subheader("📊 Excel-Tabelle erstellen")

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

    if st.button("📥 Excel generieren"):
        df = pd.DataFrame(data, columns=columns)
        file_name = "monti_excel_tabelle.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button("📥 Excel-Datei herunterladen", f, file_name=file_name)
        os.remove(file_name)

# PDF-Modus mit Bildern
if doc_type == "PDF (Text + Bilder)":
    st.subheader("📄 PDF mit Bildern und Text erstellen")

    format_option = st.selectbox("Wähle dein Buchformat (KDP-kompatibel):", ["6 x 9 Zoll", "7 x 10 Zoll", "8.25 x 11 Zoll", "A5"])
    format_mapping = {
        "6 x 9 Zoll": (152, 229),
        "7 x 10 Zoll": (178, 254),
        "8.25 x 11 Zoll": (210, 280),
        "A5": (148, 210)
    }
    page_w, page_h = format_mapping[format_option]

    seiten = st.number_input("Wie viele Seiten soll dein PDF haben?", min_value=1, max_value=20, value=2)

    seiten_content = []
    for i in range(seiten):
        st.markdown(f"### Seite {i+1}")
        text = st.text_area(f"Text für Seite {i+1}", key=f"text_{i}")
        image = st.file_uploader(f"Bild für Seite {i+1} hochladen", type=["png", "jpg", "jpeg"], key=f"img_{i}")
        layout_style = st.selectbox(f"Layout-Stil für Seite {i+1}", ["Bild oben, Text unten", "Text oben, Bild unten", "Text neben Bild", "Nur Text", "Nur Bild"], key=f"layout_{i}")
        seiten_content.append((text, image, layout_style))

    if st.button("📄 PDF generieren"):
        pdf = FPDF(orientation="P", unit="mm", format=(page_w, page_h))
        pdf.set_auto_page_break(auto=True, margin=10)

        for idx, (text, img_file, layout) in enumerate(seiten_content):
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            if layout == "Nur Text":
                pdf.multi_cell(0, 10, text, align='C')
            elif layout == "Nur Bild" and img_file:
                img = Image.open(img_file)
                img_path = f"temp_img_{idx}.png"
                img.save(img_path)
                pdf.image(img_path, x=10, y=20, w=page_w - 20)
                os.remove(img_path)
            elif layout == "Text oben, Bild unten":
                pdf.multi_cell(0, 10, text, align='C')
                if img_file:
                    img = Image.open(img_file)
                    img_path = f"temp_img_{idx}.png"
                    img.save(img_path)
                    pdf.image(img_path, x=10, y=pdf.get_y() + 10, w=page_w - 20)
                    os.remove(img_path)
            elif layout == "Bild oben, Text unten":
                if img_file:
                    img = Image.open(img_file)
                    img_path = f"temp_img_{idx}.png"
                    img.save(img_path)
                    pdf.image(img_path, x=10, y=20, w=page_w - 20)
                    os.remove(img_path)
                    pdf.set_y(130)
                pdf.multi_cell(0, 10, text, align='C')
            elif layout == "Text neben Bild" and img_file:
                pdf.multi_cell(100, 10, text)
                img = Image.open(img_file)
                img_path = f"temp_img_{idx}.png"
                img.save(img_path)
                pdf.image(img_path, x=110, y=pdf.get_y() - 10, w=60)
                os.remove(img_path)

        pdf_file = "monti_dokument.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 PDF-Datei herunterladen", f, file_name=pdf_file)
        os.remove(pdf_file)
