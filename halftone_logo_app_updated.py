# halftone_logo_app_updated.py
import streamlit as st
import svgwrite
import xml.etree.ElementTree as ET
from svgpathtools import parse_path, svg2paths2
import zipfile
import io
import base64

st.set_page_config(layout="wide")
st.title("🎨 تأثير Halftone داخل شكل شعار")

st.markdown("""
### 🆙 ارفع ملفي SVG:
- 🔺 الشعار الأساسي (فقط SVG - شكل خارجي مغلق)
- 🔷 الشكل المتكرر داخل الشعار (فقط SVG)
""")

col1, col2 = st.columns(2)

logo_svg_file = col1.file_uploader("🔺 ارفع الشعار الأساسي (فقط SVG - شكل خارجي مغلق)", type=["svg"])
tile_svg_file = col2.file_uploader("🔷 ارفع الشكل المتكرر داخل الشعار (فقط SVG)", type=["svg"])

repetitions = st.slider("عدد التكرار (كلما زاد قل الحجم)", 10, 200, 80)
fg_color = st.color_picker("🎨 اختر لون الشكل", "#000000")
bg_color = st.color_picker("🧱 اختر لون الخلفية", "#ffffff")

canvas_size = 2000

if logo_svg_file and tile_svg_file:
    try:
        logo_svg_content = logo_svg_file.read().decode("utf-8")
        tile_svg_content = tile_svg_file.read().decode("utf-8")

        logo_paths, logo_attributes, svg_attributes = svg2paths2(io.StringIO(logo_svg_content))
        tile_paths, _, _ = svg2paths2(io.StringIO(tile_svg_content))

        if not logo_paths or not tile_paths:
            st.error("❌ لم يتم العثور على عناصر <path> في ملف SVG.")
        else:
            logo_path = logo_paths[0]
            tile_path = tile_paths[0]

            xmin, xmax, ymin, ymax = logo_path.bbox()
            logo_width = xmax - xmin
            logo_height = ymax - ymin
            scale = min((canvas_size * 0.8) / logo_width, (canvas_size * 0.8) / logo_height)

            offset_x = (canvas_size - logo_width * scale) / 2 - xmin * scale
            offset_y = (canvas_size - logo_height * scale) / 2 - ymin * scale

            dwg = svgwrite.Drawing(size=(canvas_size, canvas_size))
            dwg.add(dwg.rect(insert=(0, 0), size=(canvas_size, canvas_size), fill=bg_color))

            step_x = step_y = canvas_size / repetitions

            for row in range(repetitions):
                for col in range(repetitions):
                    cx = col * step_x + step_x / 2
                    cy = row * step_y + step_y / 2
                    scale_factor = 1 - ((abs(cx - canvas_size / 2) + abs(cy - canvas_size / 2)) / (canvas_size))
                    tile_size = step_x * 0.6 * scale_factor

                    tile_group = svgwrite.container.Group(fill=fg_color)
                    for segment in tile_path:
                        tile_group.add(dwg.path(d=segment.d(), transform=f"translate({cx - tile_size/2},{cy - tile_size/2}) scale({tile_size/100})"))
                    center_point = complex(cx, cy)
                    if logo_path.contains(center_point):
                        dwg.add(tile_group)

            final_svg = dwg.tostring()

            st.markdown("### 🖼️ المعاينة:")
            st.components.v1.html(final_svg, height=700)

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                zip_file.writestr("halftone_result.svg", final_svg)

            st.download_button("📥 تحميل النتيجة كـ SVG", zip_buffer.getvalue(), file_name="halftone_output.zip", mime="application/zip")

    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")
