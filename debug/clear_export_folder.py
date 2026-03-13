import os
import shutil

def clear_export_folder():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_folder = os.path.join(base_dir, "export")

    if not os.path.exists(export_folder):
        return

    deleted_files = 0
    for filename in os.listdir(export_folder):
        file_path = os.path.join(export_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
                deleted_files += 1
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                deleted_files += 1
        except Exception as e:
            print(f"⚠️ ลบไฟล์ {filename} ไม่ได้: {e}")

    print(f"✅ ลบไฟล์ทั้งหมดใน 'export' สำเร็จ ({deleted_files} รายการ)")
    
clear_export_folder()
