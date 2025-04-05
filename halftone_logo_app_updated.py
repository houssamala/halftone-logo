import streamlit as st
import xml.etree.ElementTree as ET
import numpy as np
import io

st.title("توليد Halftone داخل شكل متجه (SVG فقط)")

uploaded_file = st.file_uploader("ارفع ملف الشعار بصيغة SVG فقط", type=["svg"])

if uploaded_file:
    gradient_type = st.selectbox("نوع التدرج", ["دائري", "أفقي", "عمودي"])
    tile_spacing = st.slider("عدد التكرارات (كلما قلّ الرقم زادت الكثافة)", 5, 50, 10)
    min_radius = st.slider("أصغر نصف قطر", 1, 10, 2)
    max_radius = st.slider("أكبر نصف قطر", 5, 50, 15)

    svg_data = uploaded_file.read().decode("utf-8")
    tree = ET.ElementTree(ET.fromstring(svg_data))
    root = tree.getroot()

    # استخراج حجم الـ SVG
    svg_width = int(root.attrib.get("width", "600").replace("px", ""))
    svg_height = int(root.attrib.get("height", "600").replace("px", ""))
    output_size = max(svg_width, svg_height)

    # استخدام viewBox أو fallback
    vb = root.attrib.get("viewBox", f"0 0 {output_size} {output_size}")
    _, _, width, height = [float(x) for x in vb.strip().split()]

    # سنولد نقاط داخل مساحة العمل بالكامل (المتجه داخلها)
    center_x = width / 2
    center_y = height / 2

    halftone_circles = []
    for y in range(0, int(height), tile_spacing):
        for x in range(0, int(width), tile_spacing):
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
            radius = max(min_radius, int(max_radius * scale))

            # توليد دائرة مؤقتة (بدون فحص تقاطع مع path الحقيقي حالياً)
            halftone_circles.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="black"/>')

    new_svg = f'''
    <svg width="{int(width)}" height="{int(height)}" xmlns="http://www.w3.org/2000/svg">
        {"".join(halftone_circles)}
    </svg>
    '''

    # عرض وتحميل الناتج
    st.download_button("تحميل SVG", new_svg, file_name="halftone_from_svg.svg", mime="image/svg+xml")
    st.markdown(f'<div style="border:1px solid #ccc;">{new_svg}</div>', unsafe_allow_html=True)