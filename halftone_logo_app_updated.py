# halftone_fill_with_scaling.py
import streamlit as st
from PIL import Image
import numpy as np
import io

st.title("تعبئة كاملة مع تأثير Halftone حقيقي (الحجم يتدرج حسب البعد)")

uploaded_file = st.file_uploader("ارفع صورة الشعار (شكل داكن على خلفية فاتحة)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("L")
    output_size = 600
    center_x, center_y = output_size // 2, output_size // 2

    img_resized = image.resize((output_size, output_size))
    mask = np.array(img_resized) < 128

    tile = image.convert("L").resize((50, 50))
    tile = tile.crop((5, 5, 45, 45))  # إزالة الحواف

    final_img = Image.new("L", (output_size, output_size), "white")
    max_dist = np.hypot(center_x, center_y)

    base_step = 12  # بين التكرارات
    min_size = 4
    max_size = 12

    for y in range(0, output_size, base_step):
        for x in range(0, output_size, base_step):
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
                tile_scaled = tile.resize((tile_size, tile_size), Image.LANCZOS)
                final_img.paste(tile_scaled, (px, py))

    st.image(final_img, caption="Halftone بتعبئة كاملة وتدرج بالحجم", use_container_width=True)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    st.download_button("تحميل الصورة", buf.getvalue(), file_name="halftone_filled_scaled.png", mime="image/png")
