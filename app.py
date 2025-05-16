import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
from PyPDF2 import PdfReader
import base64
from PIL import Image

# Fonts registrieren
pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('NotoSans', 'fonts/NotoSans-Regular.ttf'))

st.set_page_config(page_title="Monti - Dokumenten-Bot", layout="wide")

# Stil
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

# Layout: Zwei Spalten
col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://i.postimg.cc/9Q4sX3M5/Kein-Titel-Lesezeichen.png", width=280)

with col2:
    st.markdown("<div class='title'><h1>📄 Monti – Dein intelligenter PDF-Generator</h1></div>", unsafe_allow_html=True)

    option = st.selectbox("Was möchtest du erstellen?", ["E-Book", "Rechnung", "Brief", "Urkunde", "Präsentation"])

    font_size = st.slider("Schriftgröße", 8, 24, 12)
    line_spacing = st.slider("Zeilenabstand", 10, 30, 16)
    alignment = st.selectbox("Ausrichtung", ["Links", "Zentriert", "Rechts"])
    font_choice = st.selectbox("Schriftart", ["DejaVuSans", "NotoSans"])
    design_choice = st.selectbox("Design-Vorlage", ["Business", "Kreativ", "Minimalistisch"])

    logo_file = st.file_uploader("Firmenlogo hochladen (optional)", type=["jpg", "jpeg", "png"])

    align_map = {"Links": 0, "Zentriert": 1, "Rechts": 2}
    color_map = {
        "Business": colors.HexColor("#2E4053"),
        "Kreativ": colors.HexColor("#8E44AD"),
        "Minimalistisch": colors.black
    }

    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName=font_choice,
        fontSize=font_size + 4,
        leading=line_spacing + 2,
        alignment=align_map[alignment],
        textColor=color_map[design_choice]
    )

    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        name='Custom',
        parent=styles['Normal'],
        fontName=font_choice,
        fontSize=font_size,
        leading=line_spacing,
        alignment=align_map[alignment]
    )

    def convert_uploaded_image(uploaded_file):
        image = Image.open(uploaded_file)
        image.thumbnail((400, 300))
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        return image_bytes

    def generate_ebook(text, chapter_image_map):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        lines = text.split("\n")
        current_chapter = None

        for line in lines:
            if line.strip().startswith("#"):
                current_chapter = line.strip('# ').strip().lower()
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(current_chapter.title(), title_style))

                for key in chapter_image_map:
                    if key.lower() == current_chapter:
                        try:
                            img_data = convert_uploaded_image(chapter_image_map[key]['file'])
                            position = chapter_image_map[key]['position']
                            if position == "Unter Text":
                                elements.append(Spacer(1, 12))
                                elements.append(RLImage(img_data, width=12*cm, height=8*cm))
                            elif position == "Über Text":
                                elements.insert(-1, RLImage(img_data, width=12*cm, height=8*cm))
                            elif position == "Neben Text":
                                table = Table([
                                    [RLImage(img_data, width=6*cm, height=4*cm), Paragraph(current_chapter.title(), title_style)]
                                ])
                                elements[-1] = table
                            elif position == "Hinter Text":
                                elements.append(Spacer(1, 12))
                                elements.append(Paragraph("[Bild hinter Text – aktuell nicht unterstützt in PDF]", custom_style))
                        except Exception as e:
                            elements.append(Paragraph(f"⚠️ Bild konnte nicht geladen werden: {e}", custom_style))
                        break
            else:
                elements.append(Paragraph(line.strip(), custom_style))
                elements.append(Spacer(1, 6))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def generate_invoice(data, company_info, logo, ust):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        if logo:
            img_data = convert_uploaded_image(logo)
            elements.append(RLImage(img_data, width=4*cm, height=2*cm))

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Rechnung", title_style))
        elements.append(Spacer(1, 12))

        for info in company_info:
            elements.append(Paragraph(info, custom_style))
        elements.append(Spacer(1, 12))

        invoice_data = [["Beschreibung", "Menge", "Einzelpreis", "Gesamt"]] + [
            [item['beschreibung'], item['menge'], item['preis'], item['gesamt']] for item in data
        ]

        netto = sum(float(i['gesamt'].replace(' €', '')) for i in data)
        ust_betrag = (netto * ust / 100)
        brutto = netto + ust_betrag

        invoice_data.append(["", "", "Netto", f"{netto:.2f} €"])
        invoice_data.append(["", "", f"USt ({ust:.0f}%)", f"{ust_betrag:.2f} €"])
        invoice_data.append(["", "", "Brutto", f"{brutto:.2f} €"])

        table = Table(invoice_data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), color_map[design_choice]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), font_choice)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    text_input = st.text_area("Dein Text (mit # für Kapitelüberschriften)", height=300)
    chapter_image_map = {}

    ust = 0
    if option == "E-Book":
        image_files = st.file_uploader("Bilder hochladen", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if image_files:
            for i, img in enumerate(image_files):
                chapter = st.text_input(f"Zu welchem Kapitel gehört dieses Bild? ({img.name})", key=f"chapter_input_{i}")
                position = st.selectbox("Bildposition", ["Unter Text", "Über Text", "Neben Text", "Hinter Text"], key=f"position_{i}")
                if chapter:
                    chapter_image_map[chapter.lower()] = {"file": img, "position": position}

    elif option == "Rechnung":
        st.subheader("Rechnungsdaten")
        firmendaten = [
            st.text_input("Firmenname"),
            st.text_input("Rechnungsadresse"),
            st.text_input("UID-Nummer"),
            st.text_input("Bankverbindung (IBAN, BIC etc.)")
        ]
        ust = st.number_input("Umsatzsteuer (%)", min_value=0.0, max_value=100.0, value=20.0)

        produkte = []
        for i in range(1, 4):
            beschreibung = st.text_input(f"Produktbeschreibung {i}", key=f"beschreibung_{i}")
            menge = st.text_input(f"Menge {i}", key=f"menge_{i}")
            preis = st.text_input(f"Einzelpreis {i} (€)", key=f"preis_{i}")
            try:
                gesamt = f"{float(menge) * float(preis):.2f} €"
            except:
                gesamt = "0.00 €"
            produkte.append({
                "beschreibung": beschreibung,
                "menge": menge,
                "preis": preis,
                "gesamt": gesamt
            })

    if st.button("📅 PDF erstellen"):
        if option == "E-Book":
            if not text_input:
                st.warning("Bitte Text eingeben.")
            else:
                pdf_buffer = generate_ebook(text_input, chapter_image_map)
                st.download_button("📘 E-Book herunterladen", data=pdf_buffer, file_name="ebook.pdf", mime="application/pdf")

                with st.expander("📄 Vorschau anzeigen"):
                    base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)

        elif option == "Rechnung":
            pdf_buffer = generate_invoice(produkte, firmendaten, logo_file, ust)
            st.download_button("🩾 Rechnung herunterladen", data=pdf_buffer, file_name="rechnung.pdf", mime="application/pdf")

            with st.expander("📄 Vorschau anzeigen"):
                base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

        else:
            st.info("Dieses Dokumentenformat wird bald unterstützt.")
