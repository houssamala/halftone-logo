import streamlit as st
from xml.dom import minidom
from PIL import Image
import numpy as np
import io
import zipfile
import base64

st.set_page_config(page_title="Halftone Generator", layout="centered")
st.title("🎨 توليد تأثير Halftone من صورة أو SVG")

uploaded_file = st.file_uploader("🔼 ارفع شعارك (PNG, JPG, SVG)", type=["svg", "png", "jpg", "jpeg"])

if uploaded_file:
    st.sidebar.header("⚙️ الإعدادات")
    output_size = 600
    step = st.sidebar.slider("📏 عدد التكرارات (كل كم بكسل)", 20, 100, 60)
    scale = st.sidebar.slider("🔍 الحجم النسبي لكل عنصر", 0.2, 2.0, 0.6)
    bg_color = st.sidebar.color_picker("🎨 لون الخلفية", "#FFFFFF")

    svg_elements = []
    element_width = 40
    element_height = 40

    if uploaded_file.name.lower().endswith(".svg"):
        # ----------- دعم SVG ----------
        svg_data = uploaded_file.read().decode("utf-8")
        doc = minidom.parseString(svg_data)
        supported_tags = ["path", "rect", "circle", "ellipse", "polygon", "polyline"]

        found = False
        for tag in supported_tags:
            nodes = doc.getElementsByTagName(tag)
            for node in nodes:
                node_str = node.toxml()
                svg_elements.append(node_str)
                found = True

        if not found:
            st.error("❌ لم يتم العثور على عناصر قابلة للتكرار داخل ملف SVG.")
            st.stop()

    else:
        # ---------- دعم الصور ----------
        img = Image.open(uploaded_file).convert("RGBA").resize((element_width, element_height))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        img_href = f'data:image/png;base64,{img_b64}'
        svg_elements.append(f'<image href="{img_href}" width="{element_width}" height="{element_height}"/>')

    # ----------- بناء SVG مع توسيط ----------
    canvas = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{output_size}" height="{output_size}" viewBox="0 0 {output_size} {output_size}">']
    canvas.append(f'<rect width="100%" height="100%" fill="{bg_color}"/>')

    cols = output_size // step
    rows = output_size // step
    offset_x = (output_size - cols * step) // 2
    offset_y = (output_size - rows * step) // 2

    for row in range(rows):
        for col in range(cols):
            x = offset_x + col * step
            y = offset_y + row * step
            g = f'<g transform="translate({x},{y}) scale({scale})">' + ''.join(svg_elements) + '</g>'
            canvas.append(g)

    canvas.append('</svg>')
    final_svg = "\n".join(canvas)

    # عرض SVG مباشرة داخل الصفحة
    st.markdown("### 🖼️ المعاينة:")
    st.components.v1.html(final_svg, height=output_size + 20)

    # تحميل كـ SVG داخل ملف ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr("halftone_output.svg", final_svg)
    zip_buffer.seek(0)

    st.download_button(
        "📥 تحميل النتيجة كـ SVG",
        zip_buffer,
        file_name="halftone_output.zip",
        mime="application/zip"
    )
