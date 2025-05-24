import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
from PIL import Image
import tempfile
import os
import base64
import re

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

    font_size = st.slider("Schriftgröße", 8, 24, 12)
    line_spacing = st.slider("Zeilenabstand", 10, 30, 16)
    alignment = st.selectbox("Ausrichtung", ["Links", "Zentriert", "Rechts"])
    font_choice = st.selectbox("Schriftart", ["DejaVuSans", "NotoSans"])
    design_choice = st.selectbox("Design-Vorlage", ["Business", "Kreativ", "Minimalistisch"])

    page_size_option = st.selectbox("Seitenformat", ["A4", "KDP 6x9 inch", "KDP 8.5x11 inch"])
    page_sizes = {
        "A4": A4,
        "KDP 6x9 inch": (6*inch, 9*inch),
        "KDP 8.5x11 inch": (8.5*inch, 11*inch)
    }

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

    def extract_chapter_titles(text):
        return [line.strip('# ').strip() for line in text.split('\n') if line.strip().startswith('#')]

    def generate_ebook(text, chapter_image_map, page_size):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=page_size)
        elements = []

        lines = text.split("\n")
        current_chapter = None
        chapter_content = []

        def render_chapter(title, content, image_info):
    chapter_elements = []
    width = image_info.get('width', 12) if image_info else 12

    if image_info and image_info['position'] == "Über Text":
        img_path = convert_uploaded_image(image_info['file'], max_width=width)
        if img_path:
            chapter_elements.append(RLImage(img_path, width=width*cm))
        chapter_elements.append(Spacer(1, 6))

    chapter_elements.append(Paragraph(title.title(), title_style))
    chapter_elements.append(Spacer(1, 6))

    if image_info and image_info['position'] == "Neben Text":
        img_path = convert_uploaded_image(image_info['file'], max_width=width)
        if img_path:
            try:
                img = RLImage(img_path, width=width*cm)
                text_para = Paragraph("<br/>".join(content), custom_style)
                text_table = Table(
                    [[img, text_para]],
                    colWidths=[width*cm, None]
                )
                text_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                chapter_elements.append(text_table)
                chapter_elements.append(Spacer(1, 6))
                return chapter_elements
            except Exception as e:
                chapter_elements.append(Paragraph("[Fehler bei Tabellenlayout mit Bild]", custom_style))

    for line in content:
        chapter_elements.append(Paragraph(line, custom_style))
        chapter_elements.append(Spacer(1, 6))

    if image_info and image_info['position'] == "Unter Text":
        img_path = convert_uploaded_image(image_info['file'], max_width=width)
        if img_path:
            chapter_elements.append(Spacer(1, 12))
            chapter_elements.append(RLImage(img_path, width=width*cm))

    chapter_elements.append(Spacer(1, 12))
    return chapter_elements
                except Exception as e:
                    chapter_elements.append(Paragraph("[Fehler bei Tabellenlayout mit Bild]", custom_style))

        for line in content:
            chapter_elements.append(Paragraph(line, custom_style))
            chapter_elements.append(Spacer(1, 6))

        if image_info and image_info['position'] == "Unter Text":
            img_path = convert_uploaded_image(image_info['file'], max_width=width)
            if img_path:
                chapter_elements.append(Spacer(1, 12))
                chapter_elements.append(RLImage(img_path, width=width*cm))

        chapter_elements.append(Spacer(1, 12))
        return chapter_elements
            except Exception as e:
                chapter_elements.append(Paragraph("[Fehler bei Tabellenlayout mit Bild]", custom_style))

    for line in content:
        chapter_elements.append(Paragraph(line, custom_style))
        chapter_elements.append(Spacer(1, 6))

    if image_info and image_info['position'] == "Unter Text":
        img_path = convert_uploaded_image(image_info['file'], max_width=width)
        if img_path:
            chapter_elements.append(Spacer(1, 12))
            chapter_elements.append(RLImage(img_path, width=width*cm))

    chapter_elements.append(Spacer(1, 12))
    return chapter_elements
                    except Exception as e:
                        chapter_elements.append(Paragraph("[Fehler bei Tabellenlayout mit Bild]", custom_style))
                        for line in content:
                            chapter_elements.append(Paragraph(line, custom_style))
                            chapter_elements.append(Spacer(1, 6))
                        return chapter_elements
                else:
                    for line in content:
                        chapter_elements.append(Paragraph(line, custom_style))
                        chapter_elements.append(Spacer(1, 6))
                chapter_elements.append(Spacer(1, 6))
            chapter_elements.append(text_table)
                        return chapter_elements
                except Exception as e:
                        chapter_elements.append(Paragraph("[Fehler bei Tabellenlayout mit Bild]", custom_style))
                        for line in content:
                            chapter_elements.append(Paragraph(line, custom_style))
                        return chapter_elements
                        
            
            return chapter_elements

        for line in lines:
            if line.strip().startswith("#"):
                if current_chapter:
                    image_info = chapter_image_map.get(current_chapter.lower())
                    elements.extend(render_chapter(current_chapter, chapter_content, image_info))
                current_chapter = line.strip('# ').strip()
                chapter_content = []
            else:
                chapter_content.append(line.strip())

        if current_chapter:
            image_info = chapter_image_map.get(current_chapter.lower())
            elements.extend(render_chapter(current_chapter, chapter_content, image_info))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    text_input = st.text_area("Dein Text mit #Kapitelüberschrift\nBeispiel:\n# Einleitung\nHier beginnt dein Text...", height=300)
    chapter_image_map = {}
    chapter_titles = extract_chapter_titles(text_input)

    if option == "E-Book":
        st.markdown("**📸 Bilder hochladen und dem passenden Kapitel zuordnen:**")
        image_files = st.file_uploader("Bilder auswählen", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if image_files and chapter_titles:
            for i, img in enumerate(image_files):
                with st.expander(f"Bild-Einstellungen: {img.name}"):
                    st.image(img, width=200)
                    chapter = st.selectbox("Kapitel für dieses Bild auswählen", chapter_titles, key=f"ch_{i}")
                    position = st.selectbox("Position im Kapitel", ["Unter Text", "Über Text", "Neben Text"], key=f"pos_{i}")
                    width = st.slider("Bildbreite in cm", 4, 16, 12, key=f"width_{i}")
                    if chapter:
                        chapter_image_map[chapter.lower()] = {"file": img, "position": position, "width": width}
        elif image_files:
            st.warning("Bitte gib zuerst Text mit Kapitelüberschriften (# Kapitelname) ein, um Kapitel zu erkennen.")

    if st.button("📄 PDF erstellen"):
        if not text_input:
            st.warning("Bitte Text eingeben.")
        else:
            pdf_buffer = generate_ebook(text_input, chapter_image_map, page_sizes[page_size_option])
            st.download_button("📘 E-Book herunterladen", data=pdf_buffer, file_name="ebook.pdf", mime="application/pdf")
            with st.expander("📄 Vorschau anzeigen"):
                base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
