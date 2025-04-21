# halftone_logo_no_overlap.py
import streamlit as st
from PIL import Image
import numpy as np
import io

st.title("تأثير Halftone داخل شكل الشعار بدون تداخل")

uploaded_file = st.file_uploader("ارفع صورة الشعار (شكل مغلق بلون داكن على خلفية فاتحة)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("L")
    output_size = 600
    center_x, center_y = output_size // 2, output_size // 2

    # Resize and create mask
    img_resized = image.resize((output_size, output_size))
    mask_resized = np.array(img_resized) < 128  # داخل الشكل = True

    # إعداد التايل
    tile = image.convert("L").resize((50, 50))
    tile = tile.crop((5, 5, 45, 45))  # إزالة الحواف 10px

    final_img = Image.new("L", (output_size, output_size), "white")
    max_radius = np.hypot(center_x, center_y)

    step = 12  # تباعد الشبكة
    for y in range(0, output_size, step):
        for x in range(0, output_size, step):
            dist = np.hypot(x - center_x, y - center_y)
            scale = 1.0 - (dist / max_radius)
            tile_size_scaled = max(4, int((step - 2) * scale))  # يجب أن يكون أصغر من التباعد

            paste_x = x - tile_size_scaled // 2
            paste_y = y - tile_size_scaled // 2

            if (paste_x < 0 or paste_y < 0 or 
                paste_x + tile_size_scaled > output_size or 
                paste_y + tile_size_scaled > output_size):
                continue

            tile_mask_area = mask_resized[paste_y:paste_y + tile_size_scaled, paste_x:paste_x + tile_size_scaled]
            if tile_mask_area.shape != (tile_size_scaled, tile_size_scaled):
                continue

            inside_ratio = np.mean(tile_mask_area)
            if inside_ratio >= 0.9:
                tile_scaled = tile.resize((tile_size_scaled, tile_size_scaled), Image.LANCZOS)
                final_img.paste(tile_scaled, (paste_x, paste_y))

    # عرض وتحميل الصورة
    st.image(final_img, caption="الناتج النهائي", use_container_width=True)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    st.download_button("تحميل الصورة", buf.getvalue(), file_name="halftone_no_overlap.png", mime="image/png")
