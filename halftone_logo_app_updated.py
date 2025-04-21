import streamlit as st
from xml.dom import minidom
import io
import zipfile

st.set_page_config(page_title="SVG Halftone Generator", layout="centered")
st.title("🎯 مولد تكرارات شعار SVG (بدون صور مرتبطة)")

uploaded_file = st.file_uploader("🔺 ارفع شعار بصيغة SVG", type=["svg"])

if uploaded_file:
    svg_content = uploaded_file.read().decode("utf-8")

    try:
        # استخراج <path> من الملف
        doc = minidom.parseString(svg_content)
        paths = doc.getElementsByTagName('path')
        if not paths:
            st.error("❌ لم يتم العثور على أي عناصر <path> داخل ملف SVG.")
        else:
            # إعدادات التكرار
            st.sidebar.header("⚙️ الإعدادات")
            output_size = 600
            step = st.sidebar.slider("📏 المسافة بين التكرارات", 20, 100, 60)
            scale = st.sidebar.slider("🔍 حجم كل تكرار", 0.1, 1.5, 0.4)

            bg_color = st.sidebar.color_picker("🌈 لون الخلفية", "#FFFFFF")

            # تحضير مسارات الشعار
            path_elements = []
            for p in paths:
                d = p.getAttribute('d')
                fill = p.getAttribute('fill') or "#000000"
                path_elements.append(f'<path d="{d}" fill="{fill}" />')

            # بناء SVG النهائي
            svg_lines = [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{output_size}" height="{output_size}" viewBox="0 0 {output_size} {output_size}">',
                f'<rect width="100%" height="100%" fill="{bg_color}" />'
            ]

            for y in range(0, output_size, step):
                for x in range(0, output_size, step):
                    g = f'<g transform="translate({x},{y}) scale({scale})">' + ''.join(path_elements) + '</g>'
                    svg_lines.append(g)

            svg_lines.append('</svg>')
            final_svg = '\n'.join(svg_lines)

            # عرض
            st.markdown("### 🖼️ المعاينة:")
            st.components.v1.html(final_svg, height=output_size + 20)

            # تحميل
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                zipf.writestr("halftone_output.svg", final_svg)
            zip_buffer.seek(0)

            st.download_button("📥 تحميل SVG", data=zip_buffer, file_name="halftone_output.zip", mime="application/zip")

    except Exception as e:
        st.error(f"🚫 خطأ أثناء معالجة SVG: {e}")
