import streamlit as st
import numpy as np
import tempfile
from svgpathtools import svg2paths2
import base64
from matplotlib.path import Path as MplPath

st.title("تكرار شعار SVG داخل نفسه باستخدام <use> وتأثير Halftone")

uploaded_svg = st.file_uploader("ارفع شعارك بصيغة SVG", type=["svg"])

if uploaded_svg:
    gradient_type = st.selectbox("نوع التدرج", ["دائري", "أفقي", "عمودي"])
    spacing = st.slider("عدد التكرارات (كلما قل الرقم زادت الكثافة)", 5, 80, 20)
    min_size = st.slider("أصغر حجم للشعار", 5, 40, 10)
    max_size = st.slider("أكبر حجم للشعار", 10, 100, 30)
    bg_color = st.color_picker("لون الخلفية", "#FFFFFF")
    fill_color = st.color_picker("لون الشعار", "#000000")

    # حفظ ملف SVG مؤقتًا
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmp:
        tmp.write(uploaded_svg.read())
        tmp_path = tmp.name

    # استخراج المسارات
    paths, attributes, svg_attributes = svg2paths2(tmp_path)
    if not paths:
        st.error("الملف لا يحتوي على path.")
        st.stop()

    # قراءة الأبعاد من viewBox أو width/height
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

    # استخراج أول path
    original_path = paths[0]
    d_attr = original_path.d()

    # تعريف الشكل الأساسي داخل <defs>
    defs = f'<defs><path id="logo" d="{d_attr}" fill="{fill_color}" /></defs>'
    uses = [f'<rect width="100%" height="100%" fill="{bg_color}" />', defs]

    # تجهيز مسار للتحقق من التداخل
    path_points = []
    for seg in original_path:
        try:
            path_points.append((seg.start.real, seg.start.imag))
            path_points.append((seg.end.real, seg.end.imag))
        except:
            continue

    if len(path_points) < 3:
        st.error("الشعار لا يحتوي على enough points.")
        st.stop()

    shape_path = MplPath(path_points, closed=True)

    # توليد العناصر المتكررة
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
                px = x - size / 2
                py = y - size / 2

                uses.append(f'<use href="#logo" x="{px}" y="{py}" width="{size}" height="{size}" />')

    svg_out = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(width)} {int(height)}">
    {"".join(uses)}
    </svg>'''

    st.download_button("تحميل SVG الناتج", svg_out, file_name="halftone_path_repeat.svg", mime="image/svg+xml")
    st.markdown(f'<div style="border:1px solid #ccc;">{svg_out}</div>', unsafe_allow_html=True)
