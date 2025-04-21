import streamlit as st
from PIL import Image
import numpy as np
import io
import base64

st.set_page_config(page_title="Halftone Logo Generator", layout="centered")

st.markdown("## 🎨 مولّد تأثير Halftone داخل شعارك")
st.markdown("ارفع شعارك (لون داكن على خلفية فاتحة) واختر الإعدادات")

uploaded_file = st.file_uploader("🔺 ارفع الشعار (PNG أو JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # إعدادات التحكم
    st.sidebar.header("⚙️ الإعدادات")
    output_size = 600
    shape_color = st.sidebar.color_picker("🎯 لون الشعار", "#000000")
    bg_color = st.sidebar.color_picker("🌈 لون الخلفية", "#FFFFFF")

    repetition = st.sidebar.slider("📦 عدد التكرارات (أفقيًا)", 10, 60, 28)
    min_size = st.sidebar.slider("🔹 أصغر حجم", 2, 20, 3)
    max_size = st.sidebar.slider("🔸 أكبر حجم", min_size + 1, 50, 24)

    image = Image.open(uploaded_file).convert("L")
    center_x, center_y = output_size // 2, output_size // 2
    max_dist = np.hypot(center_x, center_y)

    img_resized = image.resize((output_size, output_size))
    mask = np.array(img_resized) < 128

    tile = image.convert("RGBA").resize((50, 50))
    tile = tile.crop((5, 5, 45, 45))

    # تحويل الصورة إلى base64 PNG
    buffer = io.BytesIO()
    tile.save(buffer, format="PNG")
    base64_tile = base64.b64encode(buffer.getvalue()).decode("utf-8")

    step = output_size // repetition
    svg_elements = [f'<rect width="100%" height="100%" fill="{bg_color}" />']

    for y in range(0, output_size, step):
        for x in range(0, output_size, step):
            dist = np.hypot(x - center_x, y - center_y)
            scale = 1.0 - (dist / max_dist)
            tile_size = int(min_size + (max_size - min_size) * scale)

            px = x - tile_size // 2
            py = y - tile_size // 2

            if (
                px < 0 or py < 0 or
                px + tile_size > output_size or
                py + tile_size > output_size
            ):
                continue

            tile_mask_area = mask[py:py + tile_size, px:px + tile_size]
            if tile_mask_area.shape != (tile_size, tile_size):
                continue

            inside_ratio = np.mean(tile_mask_area)
            if inside_ratio >= 0.85:
                svg_elements.append(
                    f'<image href="data:image/png;base64,{base64_tile}" '
                    f'x="{px}" y="{py}" width="{tile_size}" height="{tile_size}" />'
                )

    svg_out = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{output_size}" height="{output_size}" viewBox="0 0 {output_size} {output_size}">
    {"".join(svg_elements)}
    </svg>'''

    # عرض SVG
    st.markdown("### 🖼️ النتيجة النهائية:")
    st.components.v1.html(svg_out, height=output_size + 20)

    # تحميل SVG
    st.download_button("📥 تحميل كـ SVG", svg_out, file_name="halftone_logo.svg", mime="image/svg+xml")
