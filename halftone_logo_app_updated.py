# halftone_logo_app.py

import streamlit as st
import xml.etree.ElementTree as ET
from xml.dom import minidom
import zipfile
import io

st.set_page_config(layout="wide")
st.title("🎨 تأثير Halftone داخل شكل شعار")

# واجهة المستخدم
st.sidebar.markdown("### إعدادات التكرار")
repetitions = st.sidebar.slider("عدد التكرارات في العرض", 10, 100, 40)
bg_color = st.sidebar.color_picker("لون الخلفية", "#ffffff")
tile_color = st.sidebar.color_picker("لون الشكل", "#000000")

uploaded_shape = st.file_uploader("🔺 ارفع الشعار الأساسي (SVG فقط)", type=["svg"])
uploaded_tile = st.file_uploader("🔹 ارفع الشكل المتكرر (SVG فقط)", type=["svg"])

canvas_size = 2000

def extract_paths(svg_content):
    doc = minidom.parseString(svg_content)
    paths = doc.getElementsByTagName("path")
    path_elements = [p.toxml() for p in paths]
    svg_tag = doc.getElementsByTagName("svg")[0]

    vb = svg_tag.getAttribute("viewBox")
    if vb:
        _, _, w, h = map(float, vb.strip().split())
    else:
        w = float(svg_tag.getAttribute("width").replace("px", ""))
        h = float(svg_tag.getAttribute("height").replace("px", ""))

    return path_elements, w, h

if uploaded_shape and uploaded_tile:
    shape_svg = uploaded_shape.read().decode("utf-8")
    tile_svg = uploaded_tile.read().decode("utf-8")

    shape_paths, shape_w, shape_h = extract_paths(shape_svg)
    tile_paths, tile_w, tile_h = extract_paths(tile_svg)

    # Auto fit: تصغير العنصر حسب عدد التكرارات المطلوبة
    tile_target_width = canvas_size / repetitions
    tile_scale = tile_target_width / tile_w
    tile_target_height = tile_h * tile_scale

    cols = repetitions
    rows = int(canvas_size // tile_target_height)

    offset_x = (canvas_size - cols * tile_target_width) / 2
    offset_y = (canvas_size - rows * tile_target_height) / 2

    svg_elements = []

    for row in range(rows):
        for col in range(cols):
            x = col * tile_target_width + offset_x
            y = row * tile_target_height + offset_y

            transform = f'translate({x:.2f},{y:.2f}) scale({tile_scale:.4f})'
            g = f'<g transform="{transform}" fill="{tile_color}">' + ''.join(tile_paths) + '</g>'
            svg_elements.append(g)

    # Canvas النهائي
    final_svg = f'''
    <svg width="{canvas_size}" height="{canvas_size}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{bg_color}"/>
        <defs>
            <clipPath id="clip-shape">
                {"".join(shape_paths)}
            </clipPath>
        </defs>
        <g clip-path="url(#clip-shape)">
            {''.join(svg_elements)}
        </g>
    </svg>
    '''

    st.markdown("### 🖼️ المعاينة:")
    st.image(io.BytesIO(final_svg.encode("utf-8")), use_column_width=True)

    # تحميل SVG
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr("halftone_result.svg", final_svg)
    zip_buffer.seek(0)
    st.download_button("📥 تحميل النتيجة كـ SVG", zip_buffer, file_name="halftone_output.zip", mime="application/zip")
