import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
from PIL import Image
from io import BytesIO

# App-Titel
st.set_page_config(page_title="Monti – Dein PDF- & Excel-Generator", layout="wide")

# Hintergrundbild-ähnlicher Effekt durch breite Spalte links
col1, col2 = st.columns([1, 3], gap="large")
with col1:
    st.markdown("## ")  # Platzhalter
    st.image("https://i.postimg.cc/58fe5e1f-f59f-41b2-a43a-977c994a5823.png", use_container_width=True)

with col2:
    st.title("📘 Monti – Dein PDF- & Excel-Generator")
    st.markdown(
        "Willkommen bei **Monti**, deinem KI-Dokumenten-Assistenten. "
        "Du kannst hier Excel-Tabellen erstellen, Bilder hochladen und daraus ein "
        "strukturiertes PDF machen – z. B. für Kinderbücher, Berichte oder kreative Projekte."
    )

# Auswahl: Excel oder PDF
doc_type = st.selectbox("Was möchtest du erstellen?", ["PDF (Text + Bilder)", "Excel-Tabelle"])

# Restlicher Code bleibt unverändert
