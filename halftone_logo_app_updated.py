import streamlit as st
import numpy as np
import tempfile
from svgpathtools import svg2paths2
from matplotlib.path import Path as MplPath

st.title("تكرار شعار SVG داخل نفسه مع التوسيط في الـ Canvas")

uploaded_svg = st.file_uploader("ارفع شعارك بصيغة SVG", type=["svg"])

if uploaded_svg:
    gradient_type = st.selectbox("نوع التدرج", ["دائري", "أفقي", "عمودي"])
    spacing = st.slider("عدد التكرارات", 5, 80, 20)
    min_size = st.slider("أصغر حجم", 5, 40, 10)
    max_size = st.slider("أكبر حجم", 10, 100, 30)
    bg_color = st.color_picker("لون الخلفية", "#FFFFFF")
    fill_color = st.color_picker("لون الشعار", "#000000")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmp:
        tmp.write(uploaded_svg.read())
        tmp_path = tmp.name

    paths, attributes, svg_attributes = svg2paths2(tmp_path)
    if not paths:
        st.error("الملف لا يحتوي على path.")
        st.stop()

    try:
        if "viewBox" in svg_attributes:
            vb = list(map(float, svg_attributes["viewBox"].strip().split()))
            if len(vb) == 4:
                _, _, width, height = vb
            else:
                st.error("viewBox غير صالح.")
                st.stop()
        else:
            width = float(svg_attributes.get("width", 600))
            height = float(svg_attributes.get("height", 600))
    except:
        st.error("تعذر تحديد حجم الملف.")
        st.stop()

    center_x, center_y = width / 2, height / 2
    path = paths[0]
    d_attr = path.d()

    defs = f'<defs><path id="logo" d="{d_attr}" fill="{fill_color}" /></defs>'
    elements = [f'<rect width="100%" height="100%" fill="{bg_color}" />', defs]

    path_points = []
    for seg in path:
        path_points.append((seg.start.real, seg.start.imag))
        path_points.append((seg.end.real, seg.end.imag))

    shape_path = MplPath(path_points, closed=True)

    positions = []
    for y in range(0, int(height), spacing):
        for x in range(0, int(width), spacing):
            if shape_path.contains_point((x, y)):
                if gradient_type == "دائري":
                    dist = np.hypot(x - center_x, y - center_y)
                    max_dist = np.hypot(width, height)
                elif gradient_type == "أفقي":
                    dist = abs(x - center_x)
                    max_dist = width
                elif gradient_type == "عمودي":
                    dist = abs(y - center_y)
                    max_dist = height

                scale = 1.0 - (dist / max_dist)
                size = max(min_size, int(max_size * scale))
                positions.append((x, y, size))

    if not positions:
        st.error("لم يتم توليد أي عنصر داخل الشكل.")
        st.stop()

    all_x = [x for x, _, _ in positions]
    all_y = [y for _, y, _ in positions]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    grid_cx = (min_x + max_x) / 2
    grid_cy = (min_y + max_y) / 2

    offset_x = center_x - grid_cx
    offset_y = center_y - grid_cy

    for x, y, size in positions:
        px = x + offset_x - size / 2
        py = y + offset_y - size / 2
        elements.append(f'<use href="#logo" x="{px}" y="{py}" width="{size}" height="{size}" />')

    svg_out = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(width)} {int(height)}">
    {"".join(elements)}
    </svg>'''

    st.download_button("تحميل SVG", svg_out, file_name="halftone_centered.svg", mime="image/svg+xml")
    st.markdown(f'<div style="border:1px solid #ccc;">{svg_out}</div>', unsafe_allow_html=True)
