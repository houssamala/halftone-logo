import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
import io

st.set_page_config(page_title="تأثير Halftone", layout="wide")

st.markdown("## 🎨 تأثير Halftone داخل شكل شعار")
st.markdown("### ⬆️ ارفع ملفي SVG:")

col1, col2 = st.columns(2)

with col1:
    base_svg_file = st.file_uploader("📌 الشعار الأساسي (شكل خارجي مغلق - SVG فقط)", type=["svg"], key="base")

with col2:
    tile_svg_file = st.file_uploader("🔷 الشكل المتكرر داخل الشعار (SVG فقط)", type=["svg"], key="tile")

st.markdown("---")
st.markdown("### ⚙️ التحكم:")

tile_count = st.slider("🔁 عدد التكرارات (كلما زاد العدد صغُر الحجم)", 10, 150, 50)
tile_fill = st.color_picker("🎨 لون الشكل المتكرر", "#000000")
bg_fill = st.color_picker("🖼️ لون الخلفية", "#ffffff")

canvas_size = 2000

def extract_paths(svg_bytes):
    """استخراج جميع عناصر <path> من ملف SVG"""
    tree = ET.parse(svg_bytes)
    root = tree.getroot()
    paths = []
    for elem in root.iter():
        if "}" in elem.tag:
            tag = elem.tag.split("}")[1]
        else:
            tag = elem.tag
        if tag == "path":
            d = elem.attrib.get("d")
            if d:
                paths.append(d)
    return paths

if base_svg_file and tile_svg_file:
    base_paths = extract_paths(base_svg_file)
    tile_paths = extract_paths(tile_svg_file)

    if not base_paths:
        st.error("❌ لم يتم العثور على أي عناصر `<path>` داخل الشعار الأساسي.")
    elif not tile_paths:
        st.error("❌ لم يتم العثور على أي عناصر `<path>` داخل الشكل المتكرر.")
    else:
        spacing = canvas_size // tile_count
        offset = spacing // 2
        svg_elements = []

        # بناء الشبكة داخل مساحة 2000x2000
        for y in range(offset, canvas_size, spacing):
            for x in range(offset, canvas_size, spacing):
                for d in tile_paths:
                    svg_elements.append(f'<path d="{d}" fill="{tile_fill}" transform="translate({x},{y}) scale({spacing/100:.2f})" />')

        full_svg = f'''
        <svg xmlns="http://www.w3.org/2000/svg" width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}">
            <rect width="100%" height="100%" fill="{bg_fill}" />
            <clipPath id="clip-shape">
                {"".join([f'<path d="{d}" />' for d in base_paths])}
            </clipPath>
            <g clip-path="url(#clip-shape)">
                {"".join(svg_elements)}
            </g>
        </svg>
        '''

        st.markdown("### 🖼️ المعاينة:")
        st.image(io.BytesIO(full_svg.encode("utf-8")), use_container_width=True)

        # حفظ SVG داخل ملف مضغوط
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            zipf.writestr("halftone_result.svg", full_svg)
        zip_buffer.seek(0)

        st.download_button(
            "💾 تحميل النتيجة كـ SVG",
            zip_buffer,
            file_name="halftone_output.zip",
            mime="application/zip"
        )
