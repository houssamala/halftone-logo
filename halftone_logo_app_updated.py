import streamlit as st
import svgwrite
from xml.dom import minidom
import zipfile
import io
from svgpathtools import parse_path
from svgpathtools import svg2paths2
import cairosvg
import base64

st.set_page_config(layout="wide")
st.title("\U0001F3A8 تأثير Halftone داخل شكل شعار")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ↑ ارفع ملف SVG:
    ❌ **(فقط SVG - الشعار الأساسي / شكل خارجي مغلق)**
    """)
    logo_file = st.file_uploader("Upload SVG logo shape", type="svg", key="logo")

with col2:
    st.markdown("""
    ### ◉ ارفع الشكل المتكرر (SVG فقط)
    """)
    tile_file = st.file_uploader("Upload SVG tile shape", type="svg", key="tile")

bg_color = st.color_picker("لون الخلفية", "#ffffff")
tile_color = st.color_picker("لون الشكل المتكرر", "#000000")

repetitions = st.slider("عدد التكرارات في كل صف/عمود", 5, 200, 50)
canvas_size = 2000

if logo_file and tile_file:
    try:
        logo_svg = logo_file.read().decode("utf-8")
        tile_svg = tile_file.read().decode("utf-8")

        # Extract paths from logo
        paths, attributes, svg_attributes = svg2paths2(io.StringIO(logo_svg))
        all_logo_paths = [parse_path(attr['d']) for attr in attributes if 'd' in attr]

        if not all_logo_paths:
            st.error("\u274c SVG: لم يتم العثور على عناصر <path> داخل ملف")
        else:
            # Extract tile shape raw path
            tile_paths, tile_attrs, _ = svg2paths2(io.StringIO(tile_svg))
            tile_path = tile_paths[0] if tile_paths else None

            if tile_path is None:
                st.error("\u274c SVG: لم يتم العثور على <path> داخل الشكل المتكرر")
            else:
                dwg = svgwrite.Drawing(size=(canvas_size, canvas_size))
                dwg.add(dwg.rect(insert=(0, 0), size=(canvas_size, canvas_size), fill=bg_color))

                step = canvas_size / repetitions
                center = canvas_size / 2
                max_radius = (2 ** 0.5) * center

                for i in range(repetitions):
                    for j in range(repetitions):
                        x = i * step + step / 2
                        y = j * step + step / 2
                        dx = x - center
                        dy = y - center
                        dist = (dx**2 + dy**2)**0.5
                        scale = 1.0 - (dist / max_radius)
                        scale = max(0.1, scale)

                        for subpath in tile_path.continuous_subpaths():
                            d = subpath.d()
                            g = dwg.g(transform=f"translate({x},{y}) scale({scale})", fill=tile_color)
                            g.add(dwg.path(d=d))
                            dwg.add(g)

                final_svg = dwg.tostring()
                st.markdown("#### 🌟 المعاينة:")
                st.image(io.BytesIO(cairosvg.svg2png(bytestring=final_svg.encode("utf-8"))), use_column_width=True)

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.writestr("halftone_output.svg", final_svg)

                st.download_button(
                    "📄 تحميل النتيجة SVG",
                    zip_buffer.getvalue(),
                    file_name="halftone_output.zip",
                    mime="application/zip"
                )

    except Exception as e:
        st.exception(e)
