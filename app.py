import streamlit as st
from fpdf import FPDF
from PIL import Image
import requests
from io import BytesIO

def inch_to_mm(inch_str):
    w_inch, h_inch = map(float, inch_str.lower().replace("inch", "").split("x"))
    return round(w_inch * 25.4, 2), round(h_inch * 25.4, 2)

def create_kdp_pdf(titel, autor, jahr, format_zoll, seiten, impressum_text=None, logo=None, cover_url=None):
    width_mm, height_mm = inch_to_mm(format_zoll)
    pdf = FPDF(orientation="P", unit="mm", format=(width_mm, height_mm))
    pdf.set_auto_page_break(auto=False)

    pdf.add_page()
    if cover_url:
        try:
            response = requests.get(cover_url)
            img = Image.open(BytesIO(response.content))
            cover_path = "cover_temp.jpg"
            img.save(cover_path)
            pdf.image(cover_path, x=0, y=0, w=width_mm)
        except:
            pass
    pdf.set_font("Arial", 'B', 20)
    pdf.ln(20)
    pdf.cell(0, 20, titel.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, f"von {autor}".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')

    for seite in seiten:
        pdf.add_page()
        if logo:
            pdf.image(logo, x=width_mm - 50, y=10, w=30)
        pdf.set_font("Arial", size=14)
        if seite.get("text"):
            pdf.multi_cell(0, 10, seite["text"].encode('latin-1', 'replace').decode('latin-1'))
        if seite.get("image"):
            try:
                img = Image.open(seite["image"])
                img_path = "seite_temp.jpg"
                img.save(img_path)
                pdf.image(img_path, x=20, y=80, w=width_mm - 40)
            except:
                pdf.set_text_color(255, 0, 0)
                pdf.cell(0, 10, "Bild konnte nicht geladen werden.", ln=True)
                pdf.set_text_color(0, 0, 0)

    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, "Impressum", ln=True)
    pdf.ln(5)
    if impressum_text:
        text = impressum_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, text)
    else:
        default = (
            f"Autorin: {autor}\n"
            "Verlag: Selfpublishing / 50 AI Business Bots\n"
            f"Veröffentlichung: {jahr}\n"
            "Kontakt: kontakt@50aibusinessbots.com\n\n"
            "Alle Rechte vorbehalten. Dieses Buch oder Teile davon duerfen ohne schriftliche Genehmigung der Autorin nicht vervielfaeltigt oder verbreitet werden - weder elektronisch noch mechanisch, einschliesslich Fotokopie, Aufnahme oder Speicherung in Informationssystemen.\n\n"
            "Gedruckt durch Amazon KDP"
        )
        pdf.multi_cell(0, 8, default.encode('latin-1', 'replace').decode('latin-1'))

    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="Monti – Buchgenerator", layout="centered")
st.title("📘 Monti – Dein Buch als PDF")

st.info("Wähle ein Template oder gib deine Daten ein.")

buchtyp = st.selectbox("Wähle ein Template", [
    "Kinderbuch (10 Seiten)",
    "Malbuch (12 Seiten)",
    "Mini-Ratgeber (5 Kapitel)",
    "Workbook (7 Seiten)",
    "Notizbuch (100 Seiten)",
    "Romanvorlage (20 Seiten)"
])

formate = {
    "Kinderbuch (10 Seiten)": "7x10",
    "Malbuch (12 Seiten)": "8.25x11",
    "Mini-Ratgeber (5 Kapitel)": "6x9",
    "Workbook (7 Seiten)": "A5",
    "Notizbuch (100 Seiten)": "A5",
    "Romanvorlage (20 Seiten)": "6x9"
}

format_zoll = formate[buchtyp]
titel = st.text_input("Titel des Buches", "Mein erstes Buch")
autor = st.text_input("Autor:in", "Sarah Temmel")
jahr = st.text_input("Jahr", "2025")

seiten = []
anzahl = int(buchtyp.split("(")[1].split(" ")[0])

for i in range(anzahl):
    text = st.text_area(f"Text für Seite {i+1}", "Hier steht der Text...", key=f"text_{i}")
    image = st.file_uploader(f"Bild für Seite {i+1} (optional)", type=["jpg", "jpeg", "png"], key=f"image_{i}")
    seiten.append({"text": text, "image": image})

impressum = st.text_area("Individuelles Impressum (optional)", "")
logo = st.file_uploader("Logo für Seiten (optional)", type=["jpg", "jpeg", "png"])
cover = st.text_input("Cover-Bild (URL, optional)", "")

if st.button("📥 PDF erstellen"):
    pdf_bytes = create_kdp_pdf(titel, autor, jahr, format_zoll, seiten, impressum, logo, cover)
    st.download_button("📩 Buch herunterladen", data=pdf_bytes, file_name="monti_buch.pdf", mime="application/pdf")
