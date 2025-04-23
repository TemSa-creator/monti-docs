import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
from PIL import Image
from io import BytesIO

# App-Titel
st.set_page_config(page_title="Monti – Dein PDF- & Excel-Generator", layout="wide")

# App-Überschrift ohne Bild
st.title("📘 Monti – Dein PDF- & Excel-Generator")
st.markdown(
    "Willkommen bei **Monti**, deinem KI-Dokumenten-Assistenten. Du kannst hier Excel-Tabellen erstellen, Bilder hochladen und daraus ein strukturiertes PDF machen – z. B. für Kinderbücher, Berichte oder kreative Projekte."
)

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

# (PDF-Code bleibt unverändert)
