import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import io

st.title("تأثير Halftone داخل شكل الشعار")

uploaded_file = st.file_uploader("ارفع صورة الشعار (PNG مفرغ أو JPEG بخلفية فاتحة)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    gradient_type = st.selectbox("نوع التدرج", ["دائري", "أفقي", "عمودي"])
    tile_spacing = st.slider("عدد التكرارات (كلما قلّ الرقم زادت الكثافة)", 5, 50, 10)
    min_size = st.slider("أصغر حجم للتكرار", 2, 20, 5)
    max_size = st.slider("أكبر حجم للتكرار", 10, 100, 20)

    image_rgba = Image.open(uploaded_file).convert("RGBA")
    output_size = 600
    image_rgba = image_rgba.resize((output_size, output_size))
    r, g, b, a = image_rgba.split()

    # كشف الشعار حسب الشفافية أو التباين
    if a.getextrema()[0] < 255:
        # PNG بخلفية شفافة: استخدم alpha
        mask_resized = np.array(a) > 0
    else:
        # JPEG أو PNG غير شفاف: استخدم التباين
        image_gray = image_rgba.convert("L")
        mask_resized = np.array(image_gray) < 200  # يعتبر أي درجة داكنة شعار

    # استخراج مركز الشعار الحقيقي تلقائيًا
    coords = np.column_stack(np.where(mask_resized))
    center_y, center_x = coords.mean(axis=0).astype(int)

    # تحضير وحدة التكرار
    tile = image_rgba.resize((50, 50))
    final_img = Image.new("RGBA", (output_size, output_size), (255, 255, 255, 0))

    for y in range(0, output_size, tile_spacing):
        for x in range(0, output_size, tile_spacing):
            if not mask_resized[y, x]:
                continue

            # نوع التدرج
            if gradient_type == "دائري":
                dist = np.hypot(x - center_x, y - center_y)
                max_dist = np.hypot(output_size, output_size)
            elif gradient_type == "أفقي":
                dist = abs(x - center_x)
                max_dist = output_size
            elif gradient_type == "عمودي":
                dist = abs(y - center_y)
                max_dist = output_size

            scale = 1.0 - (dist / max_dist)
            tile_size_scaled = max(min_size, int(max_size * scale))

            paste_x = x - tile_size_scaled // 2
            paste_y = y - tile_size_scaled // 2

            if (paste_x < 0 or paste_y < 0 or 
                paste_x + tile_size_scaled > output_size or 
                paste_y + tile_size_scaled > output_size):
                continue

            submask = mask_resized[paste_y:paste_y + tile_size_scaled, paste_x:paste_x + tile_size_scaled]
            if submask.shape != (tile_size_scaled, tile_size_scaled):
                continue

            if np.all(submask):
                tile_scaled = tile.resize((tile_size_scaled, tile_size_scaled))
                final_img.paste(tile_scaled, (paste_x, paste_y), tile_scaled)

    st.image(final_img, caption="الناتج النهائي", use_column_width=True)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    st.download_button("تحميل الصورة", buf.getvalue(), file_name="halftone_result.png", mime="image/png")
