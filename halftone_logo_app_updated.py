from xml.dom import minidom
import io
import zipfile

# 1. شعارك بصيغة SVG (مثال: مثلث بسيط)
tile_svg_content = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="M10,90 L50,10 L90,90 Z" fill="black"/>
</svg>
'''

# 2. استخراج عناصر <path> من ملف SVG
doc = minidom.parseString(tile_svg_content)
paths = doc.getElementsByTagName('path')
path_elements = []

for p in paths:
    d = p.getAttribute('d')
    fill = p.getAttribute('fill') or "#000000"
    path_elements.append(f'<path d="{d}" fill="{fill}" />')

# 3. إنشاء الـ SVG الناتج مع تكرار المسار
output_size = 600
step = 50  # المسافة بين التكرارات
repeated_svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{output_size}" height="{output_size}" viewBox="0 0 {output_size} {output_size}">',
    f'<rect width="100%" height="100%" fill="#FFFFFF"/>'
]

for y in range(0, output_size, step):
    for x in range(0, output_size, step):
        group = f'<g transform="translate({x},{y}) scale(0.4)">'
        group += ''.join(path_elements)
        group += '</g>'
        repeated_svg.append(group)

repeated_svg.append('</svg>')

# 4. إخراج كملف
final_svg = '\n'.join(repeated_svg)

# 5. حفظه داخل ملف ZIP للتحميل
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, 'w') as zip_file:
    zip_file.writestr("halftone_output.svg", final_svg)

buffer.seek(0)
with open("halftone_output.zip", "wb") as f:
    f.write(buffer.read())
