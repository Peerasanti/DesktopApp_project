from matplotlib import font_manager

# แสดงรายชื่อฟอนต์ทั้งหมดที่ Matplotlib หาเจอ
for font in font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
    if "TH" in font or "Thai" in font or "Sarabun" in font or "Angsana" in font:
        print(font)