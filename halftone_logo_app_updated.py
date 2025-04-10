import streamlit as st
import numpy as np
import tempfile
from svgpathtools import svg2paths2
from svgpathtools import Path as SvgPath

st.title("Halftone داخل Path دقيق (SVG فقط)")

uploaded_file = st.file_uploader("ارفع ملف SVG يحتوي على path فقط", type=["svg"])

if uploaded_file:
    gradient_type = st.selectbox("نوع التدرج", ["دائري", "أفقي", "عمودي"])
    spacing = st.slider("عدد التكرارات (كلما قل الرقم زادت الكثافة)", 5, 50, 10)
    min_radius = st.slider("أصغر نصف قطر", 1, 10, 2)
    max_radius = st.slider("أكبر نصف قطر", 5, 50, 15)

    # حفظ الملف مؤقتًا
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # قراءة المسارات والخصائص
    paths, attributes, svg_attributes = svg2paths2(tmp_path)

    if not paths:
        st.error("الملف لا يحتوي على أي path داخل SVG.")
        st.stop()

    # محاولة استخراج الحجم من viewBox أو width/height
    try:
        if "viewBox" in svg_attributes:
            vb_values = list(map(float, svg_attributes["viewBox"].strip().split()))
            if len(vb_values) == 4:
                _, _, width, height = vb_values
            else:
                st.error("الملف يحتوي على viewBox غير صالح (يجب أن يتكون من 4 أرقام).")
                st.stop()
        else:
            width = float(svg_attributes.get("width", 600))
            height = float(svg_attributes.get("height", 600))
    except:
        st.error("تعذر تحديد حجم الملف. تأكد من وجود viewBox أو width/height.")
        st.stop()

    center_x, center_y = width / 2, height / 2
    path: SvgPath = paths[0]

    # توليد الدوائر داخل الشكل فقط
    circles = []
    for y in range(0, int(height), spacing):
        for x in range(0, int(width), spacing):
            point = complex(x, y)
            if path.contains(point):
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
                circles.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="black" />')

    svg_output = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(width)} {int(height)}">
    {''.join(circles)}
    </svg>'''

    st.download_button("تحميل SVG", svg_output, file_name="halftone_precise.svg", mime="image/svg+xml")
    st.markdown(f'<div style="border:1px solid #ccc;">{svg_output}</div>', unsafe_allow_html=True)