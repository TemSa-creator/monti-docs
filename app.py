# Der vollständige Monti-Code mit integrierter Rechnungserstellung

import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
from PIL import Image
import tempfile
import os
import base64

# Fonts registrieren
pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('NotoSans', 'fonts/NotoSans-Regular.ttf'))

st.set_page_config(page_title="Monti - Dokumenten-Bot", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
        }
        .title h1 {
            color: gold;
            font-size: 36px;
        }
        .text-area textarea {
            color: black;
            background-color: white;
            border: 1px solid black;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://i.postimg.cc/9Q4sX3M5/Kein-Titel-Lesezeichen.png", width=280)

with col2:
    st.markdown("<div class='title'><h1>📄 Monti – Dein intelligenter PDF-Generator</h1></div>", unsafe_allow_html=True)

option = st.selectbox("Was möchtest du erstellen?", ["E-Book", "Rechnung", "Brief", "Urkunde", "Präsentation"])

# Rechnungsteil
if option == "Rechnung":
    st.info("Bitte gib alle relevanten Rechnungsdetails ein. Es werden automatisch Mehrwertsteuer, Hinweistexte und Gesamtsumme berechnet.")

    firma = st.text_input("Firmenname")
    rechnungsnummer = st.text_input("Rechnungsnummer")
    datum = st.date_input("Rechnungsdatum")
    rechnungsadresse = st.text_area("Rechnungsadresse")
    uid_nummer = st.text_input("UID-Nummer")
    iban = st.text_input("IBAN für Überweisung")
    ust_option = st.selectbox("USt-Satz", ["0% (Kleinunternehmer)", "7%", "19%", "20% (AT)", "Reverse Charge"])

    if ust_option == "0% (Kleinunternehmer)":
        hinweis = "Keine Umsatzsteuer, da Kleinunternehmerregelung (§ 19 UStG)"
    elif ust_option == "Reverse Charge":
        hinweis = "Steuerschuldnerschaft des Leistungsempfängers – Reverse Charge Verfahren"
    else:
        hinweis = "zzgl. Umsatzsteuer gemäß ausgewähltem Satz"

    st.markdown(f"**Hinweis:** {hinweis}")

    produkte = []
    num_produkte = st.number_input("Anzahl der Produkte", min_value=1, step=1)
    for i in range(int(num_produkte)):
        with st.expander(f"Produkt {i+1}"):
            beschreibung = st.text_input(f"Produkt / Dienstleistung {i+1}", key=f"prod_desc_{i}")
            menge = st.number_input(f"Stückzahl {i+1}", min_value=1, key=f"prod_qty_{i}")
            preis = st.number_input(f"Nettopreis {i+1} in €", min_value=0.0, step=0.01, key=f"prod_price_{i}")
            produkte.append((beschreibung, menge, preis))

    logo_file = st.file_uploader("Firmenlogo hochladen (optional)", type=["jpg", "jpeg", "png"])

    if st.button("📄 Rechnung erstellen"):
        gesamt = 0
        table_data = [["Beschreibung", "Menge", "Einzelpreis (€)", "Nettobetrag (€)"]]
        for beschreibung, menge, preis in produkte:
            nettobetrag = menge * preis
            gesamt += nettobetrag
            table_data.append([beschreibung, str(menge), f"{preis:.2f}", f"{nettobetrag:.2f}"])

        if ust_option.endswith("%"):
            ust_satz = float(ust_option.replace("%", ""))
            ust_betrag = gesamt * ust_satz / 100
        else:
            ust_betrag = 0.0

        brutto = gesamt + ust_betrag

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        def convert_uploaded_image(uploaded_file, max_width=None):
            try:
                image = Image.open(uploaded_file).convert("RGB")
                if max_width:
                    base_width = int(max_width * cm)
                    w_percent = base_width / float(image.size[0])
                    h_size = int(float(image.size[1]) * w_percent)
                    image = image.resize((base_width, h_size), Image.Resampling.LANCZOS)
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)
                return img_byte_arr
            except Exception as e:
                st.error(f"Bildverarbeitung fehlgeschlagen: {e}")
                return None

        if logo_file:
            logo_img = convert_uploaded_image(logo_file, max_width=4)
            if logo_img:
                elements.append(RLImage(logo_img, width=4*cm))

        styles = getSampleStyleSheet()
        custom_style = ParagraphStyle(
            name='Custom',
            parent=styles['Normal'],
            fontName='DejaVuSans',
            fontSize=12,
            leading=16,
            alignment=0
        )

        elements.append(Paragraph(f"<b>{firma}</b>", custom_style))
        elements.append(Paragraph(f"Datum: {datum.strftime('%d.%m.%Y')}<br/>Rechnungsnummer: {rechnungsnummer}", custom_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Rechnung an:</b><br/>{rechnungsadresse.replace(chr(10), '<br/>')}", custom_style))
        elements.append(Spacer(1, 12))

        table = Table(table_data, colWidths=[200, 60, 80, 100])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"USt: {ust_betrag:.2f} €", custom_style))
        elements.append(Paragraph(f"<b>Gesamtbetrag: {brutto:.2f} €</b>", custom_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(hinweis, custom_style))
        elements.append(Paragraph(f"IBAN: {iban}<br/>UID: {uid_nummer}", custom_style))

        doc.build(elements)
        buffer.seek(0)
        st.download_button("📄 Rechnung herunterladen", data=buffer, file_name="rechnung.pdf", mime="application/pdf")
