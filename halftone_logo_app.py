import streamlit as st
from PIL import Image
import numpy as np
import io

st.title("تأثير Halftone داخل شكل الشعار")

uploaded_file = st.file_uploader("ارفع صورة الشعار (شكل مغلق بلون داكن على خلفية فاتحة)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # عناصر التحكم
    gradient_type = st.selectbox("نوع التدرج", ["دائري", "أفقي", "عمودي"])
    tile_spacing = st.slider("عدد التكرارات (كلما قلّ الرقم زادت الكثافة)", 5, 50, 10)
    min_size = st.slider("أصغر حجم للتكرار", 2, 20, 5)
    max_size = st.slider("أكبر حجم للتكرار", 10, 100, 20)

    # تجهيز الصورة والقناع
    image = Image.open(uploaded_file).convert("L")
    output_size = 600
    center_x, center_y = output_size // 2, output_size // 2

    img_resized = image.resize((output_size, output_size))
    mask_resized = np.array(img_resized) < 128

    tile = image.resize((50, 50))
    final_img = Image.new("L", (output_size, output_size), "white")

    for y in range(0, output_size, tile_spacing):
        for x in range(0, output_size, tile_spacing):
            if not mask_resized[y, x]:
                continue

            # حساب التدرج حسب النوع المختار
            if gradient_type == "دائري":
                dist = np.hypot(x - center_x, y - center_y)
                max_dist = np.hypot(center_x, center_y)
            elif gradient_type == "أفقي":
                dist = abs(x - center_x)
                max_dist = center_x
            elif gradient_type == "عمودي":
                dist = abs(y - center_y)
                max_dist = center_y

            scale = 1.0 - (dist / max_dist)
            tile_size_scaled = max(min_size, int(max_size * scale))

            paste_x = x - tile_size_scaled // 2
            paste_y = y - tile_size_scaled // 2

            if (paste_x < 0 or paste_y < 0 or 
                paste_x + tile_size_scaled > output_size or 
                paste_y + tile_size_scaled > output_size):
                continue

            tile_mask_area = mask_resized[paste_y:paste_y + tile_size_scaled, paste_x:paste_x + tile_size_scaled]
            if tile_mask_area.shape != (tile_size_scaled, tile_size_scaled):
                continue

            if np.all(tile_mask_area):
                tile_scaled = tile.resize((tile_size_scaled, tile_size_scaled))
                final_img.paste(tile_scaled, (paste_x, paste_y))

    st.image(final_img, caption="الناتج النهائي", use_column_width=True)

    # زر التحميل
    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    st.download_button("تحميل الصورة", buf.getvalue(), file_name="halftone_result.png", mime="image/png")