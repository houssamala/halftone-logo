import streamlit as st
from PIL import Image
import numpy as np
import io

st.title("تأثير Halftone داخل شكل الشعار بدون قص")

uploaded_file = st.file_uploader("ارفع صورة الشعار (شكل مغلق بلون داكن على خلفية فاتحة)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("L")
    output_size = 600
    center_x, center_y = output_size // 2, output_size // 2

    img_resized = image.resize((output_size, output_size))
    mask_resized = np.array(img_resized) < 128  # mask: True = داخل الشكل

    tile = image.resize((50, 50))
    final_img = Image.new("L", (output_size, output_size), "white")
    max_radius = np.hypot(center_x, center_y)

    for y in range(0, output_size, 10):
        for x in range(0, output_size, 10):
            dist = np.hypot(x - center_x, y - center_y)
            scale = 1.0 - (dist / max_radius)
            tile_size_scaled = max(5, int(20 * scale))

            paste_x = x - tile_size_scaled // 2
            paste_y = y - tile_size_scaled // 2

            # تأكد أن التكرار بالكامل داخل الصورة
            if (paste_x < 0 or paste_y < 0 or 
                paste_x + tile_size_scaled > output_size or 
                paste_y + tile_size_scaled > output_size):
                continue

            # قص mask بنفس حجم التكرار
            tile_mask_area = mask_resized[paste_y:paste_y + tile_size_scaled, paste_x:paste_x + tile_size_scaled]

            # ✅ شرط أساسي: يجب أن يكون 90% على الأقل من المساحة داخل الشكل
            inside_ratio = np.mean(tile_mask_area)
            if tile_mask_area.shape != (tile_size_scaled, tile_size_scaled):
                continue

            if inside_ratio >= 0.9:  # شرط أكثر مرونة
                tile_scaled = tile.resize((tile_size_scaled, tile_size_scaled))
                final_img.paste(tile_scaled, (paste_x, paste_y))

    st.image(final_img, caption="الناتج النهائي", use_container_width=True)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    st.download_button("تحميل الصورة", buf.getvalue(), file_name="halftone_result.png", mime="image/png")
