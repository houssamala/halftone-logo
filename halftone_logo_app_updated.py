import streamlit as st
import xml.etree.ElementTree as ET
from svgpathtools import parse_path, svg2paths
import zipfile
import io
import base64

st.set_page_config(layout="wide")
st.title("🎨 تأثير Halftone باستخدام الشعار")

canvas_size = 2000
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("📁 ارفع شعارك (PNG, JPG, SVG)", type=["png", "jpg", "jpeg", "svg"])

with col2:
    repetitions = st.slider("🔁 عدد التكرارات (بدون تداخل)", 5, 100, 40)
    shape_color = st.color_picker("🎨 لون الشكل", "#000000")
    bg_color = st.color_picker("🖼️ لون الخلفية", "#ffffff")

st.markdown("---")

def scale_paths_to_canvas(paths, viewbox, canvas_size):
    _, _, vb_width, vb_height = viewbox
    scale = min(canvas_size / vb_width, canvas_size / vb_height)
    offset_x = (canvas_size - vb_width * scale) / 2
    offset_y = (canvas_size - vb_height * scale) / 2
    scaled_paths = []

    for path in paths:
        d = ""
        for segment in path:
            segment = segment.scaled(scale)
            segment = segment.translated(offset_x + 0j + offset_y * 1j)
            d += segment.d()
        scaled_paths.append(d)
    
    return scaled_paths

def extract_paths_from_svg(svg_content):
    try:
        tree = ET.ElementTree(ET.fromstring(svg_content))
        root = tree.getroot()
        viewBox = root.attrib.get("viewBox", "0 0 1000 1000").split()
        viewBox = list(map(float, viewBox))

        paths, _ = svg2paths(io.StringIO(svg_content))
        return scale_paths_to_canvas(paths, viewBox, canvas_size)
    except Exception as e:
        st.error(f"❌ خطأ في قراءة ملف SVG: {e}")
        return []

if uploaded_file:
    file_content = uploaded_file.read()
    filename = uploaded_file.name.lower()

    if filename.endswith(".svg"):
        svg_str = file_content.decode("utf-8")
        path_data_list = extract_paths_from_svg(svg_str)

        if path_data_list:
            pattern_svg = ""
            spacing = canvas_size // repetitions

            for i in range(repetitions):
                for j in range(repetitions):
                    scale = 0.2 + (i + j) / (2 * repetitions)
                    for path_d in path_data_list:
                        transform = f"translate({j * spacing},{i * spacing}) scale({scale})"
                        pattern_svg += f'<path d="{path_d}" fill="{shape_color}" transform="{transform}"/>\n'

            final_svg = f'''
            <svg width="{canvas_size}" height="{canvas_size}" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="{bg_color}" />
                {pattern_svg}
            </svg>
            '''

            st.markdown("### 🖼️ المعاينة:")
            st.components.v1.html(final_svg, height=700, scrolling=False)

            # Export as zip
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr("halftone_result.svg", final_svg)
            st.download_button("📥 تحميل النتيجة كـ SVG", zip_buffer.getvalue(), file_name="halftone_output.zip", mime="application/zip")
        else:
            st.error("❌ SVG لا يحتوي على عناصر <path>.")
    else:
        st.warning("⚠️ حالياً هذا الكود يدعم فقط ملفات SVG لمسارات واضحة.")
