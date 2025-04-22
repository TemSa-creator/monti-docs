import streamlit as st
from urllib.parse import unquote
from fpdf import FPDF

def create_document_pdf(doc_type, data_dict, filename="monti_dokument.pdf", branding=True):
    """Erstellt ein PDF mit den übergebenen Daten."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Titel
    pdf.set_font(style='B')
    pdf.cell(0, 10, f"{doc_type.upper()}", ln=True)
    pdf.set_font(style='')

    pdf.ln(5)

    # Inhalte einfügen
    for key, value in data_dict.items():
        key_clean = key.replace("_", " ").capitalize()
        value_clean = unquote(str(value))
        pdf.multi_cell(0, 10, f"{key_clean}: {value_clean}")
        pdf.ln(1)

    pdf.ln(10)

    # Branding
    if branding:
        pdf.set_font("Arial", style='I', size=10)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, "powered by Monti", ln=True, align='R')

    pdf.output(filename)
    return filename

# Streamlit App
st.set_page_config(page_title="Monti – PDF Generator", layout="centered")
st.title("📄 Monti – Dein PDF-Dokument")

query = st.query_params

if query:
    doc_type = query.get("type", "Dokument")
    data_dict = {k: v for k, v in query.items() if k != "type"}

    st.subheader(f"Vorschau: {doc_type}")
    for key, value in data_dict.items():
        st.write(f"**{key.replace('_', ' ').capitalize()}**: {value}")

    if st.button("📥 PDF generieren"):
        filename = create_document_pdf(doc_type, data_dict)
        with open(filename, "rb") as f:
            st.download_button("📩 PDF herunterladen", f, file_name=filename, mime="application/pdf")
else:
    st.info("Bitte öffne den Link mit Datenparametern. Beispiel: `...?type=Rechnung&empfänger=Max&betrag=499`")
