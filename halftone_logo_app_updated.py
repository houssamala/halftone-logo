import streamlit as st
import numpy as np
import tempfile
from svgpathtools import svg2paths2
from svgpathtools import Path as SvgPath
import base64
from matplotlib.path import Path as MplPath

st.title("تكرار الشعار داخل شكله مع تحكم بالخلفية واللون")

uploaded_svg = st.file_uploader("ارفع الشعار المتجه (SVG)", type=["svg"])
uploaded_logo = st.file_uploader("ارفع نفس الشعار كصورة PNG/WEBP", type=["png", "webp"])

if uploaded_svg and uploaded_logo:
    gradient_type = st.selectbox("نوع التدرج", ["دائري", "أفقي", "عمودي"])
    spacing = st.slider("عدد التكرارات (كلما قل الرقم زادت الكثافة)", 5, 80, 20)
    min_size = st.slider("أصغر حجم للشعار", 5, 40, 10)
    max_size = st.slider("أكبر حجم للشعار", 10, 100, 30)
    bg_color = st.color_picker("لون الخلفية", "#FFFFFF")
    tint_color = st.color_picker("لون تأثير الشعار", "#000000")

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
    path: SvgPath = paths[0]

    points = []
    for segment in path:
        try:
            points.append((segment.start.real, segment.start.imag))
            points.append((segment.end.real, segment.end.imag))
        except:
            continue

    if len(points) < 3:
        st.error("لا يمكن تحليل الشكل لأن عدد النقاط قليل.")
        st.stop()

    mpl_path = MplPath(points, closed=True)

    image_data = uploaded_logo.read()
    b64_image = base64.b64encode(image_data).decode("utf-8")
    mime_type = "image/png" if uploaded_logo.name.endswith("png") else "image/webp"
    image_href = f"data:{mime_type};base64,{b64_image}"

    elements = [f'<rect width="100%" height="100%" fill="{bg_color}" />']
    for y in range(0, int(height), spacing):
        for x in range(0, int(width), spacing):
            if mpl_path.contains_point((x, y)):
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

                elements.append(f'''
<g>
  <filter id="tint" color-interpolation-filters="sRGB">
    <feColorMatrix type="matrix"
      values="0 0 0 0 {int(tint_color[1:3], 16)/255}
              0 0 0 0 {int(tint_color[3:5], 16)/255}
              0 0 0 0 {int(tint_color[5:7], 16)/255}
              0 0 0 1 0"/>
  </filter>
  <image href="{image_href}" x="{px}" y="{py}" width="{size}" height="{size}" filter="url(#tint)" />
</g>''')

    svg_result = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(width)} {int(height)}">
    {''.join(elements)}
    </svg>'''

    st.download_button("تحميل SVG الناتج", svg_result, file_name="halftone_canvas_colored.svg", mime="image/svg+xml")
    st.markdown(f'<div style="border:1px solid #ccc;">{svg_result}</div>', unsafe_allow_html=True)
