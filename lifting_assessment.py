def assess_lifting_risk(hand_info, actual_weight, lifting_freq_option, is_twisted):
    # ตาราง RWL (หน่วย: กิโลกรัม) ดึงตรงจากแบบฟอร์ม
    table = {
        ('เหนือหัวไหล่', 'ใกล้ตัว'): 29,
        ('เหนือหัวไหล่', 'ปานกลาง'): 24,
        ('เหนือหัวไหล่', 'เหยียดแขน'): 18,

        ('หัวไหล่ถึงเอว', 'ใกล้ตัว'): 32,
        ('หัวไหล่ถึงเอว', 'ปานกลาง'): 33,
        ('หัวไหล่ถึงเอว', 'เหยียดแขน'): 25,

        ('หัวเข่าถึงเอว', 'ใกล้ตัว'): 41,
        ('หัวเข่าถึงเอว', 'ปานกลาง'): 25,
        ('หัวเข่าถึงเอว', 'เหยียดแขน'): 18,

        ('ใต้เข่า', 'ใกล้ตัว'): 31,
        ('ใต้เข่า', 'ปานกลาง'): 23,
        ('ใต้เข่า', 'เหยียดแขน'): 16
    }

    # ดึงค่า RWL พื้นฐาน
    base_rwl = table.get((hand_info['height'], hand_info['distance']), 10)

    # คูณตัวปรับตามความถี่การยก (จากแบบฟอร์ม)
    freq_multiplier = {1: 1.0, 2: 0.75, 3: 0.6}.get(lifting_freq_option, 1.0)

    # คูณตัวปรับจากการบิดตัว (ตามแบบฟอร์ม: >45° = 0.85)
    twist_multiplier = 0.85 if is_twisted else 1.0

    # คำนวณ RWL สุดท้าย
    rwl = base_rwl * freq_multiplier * twist_multiplier

    # คำนวณ LH Index (หลีกเลี่ยงหารด้วย 0)
    lh_index = (actual_weight / rwl) * 100 if rwl > 0 else 999

    # แปลผลระดับความเสี่ยง
    if lh_index < 50:
        level = 'ระดับ 1 (ยกได้ปลอดภัย)'
        level_num = 1
    elif lh_index < 75:
        level = 'ระดับ 2 (ควรตรวจสอบ)'
        level_num = 2
    elif lh_index <= 100:
        level = 'ระดับ 3 (เริ่มเสี่ยง)'
        level_num = 3
    else:
        level = 'ระดับ 4 (อันตรายสูง)'
        level_num = 4

    return {
        'rwl': rwl,
        'lh_index': lh_index,
        'risk_level': level,
        'risk_level_num': level_num
    }

from PIL import ImageFont, ImageDraw, Image
import numpy as np

def draw_thai_text(image, text, position, font_size=28, color=(255, 255, 255)):
    """
    วาดข้อความภาษาไทยลงบนภาพ OpenCV โดยใช้ Pillow
    """
    # แปลงจาก OpenCV เป็น PIL
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)

    # โหลดฟอนต์ภาษาไทย (คุณอาจต้องเปลี่ยน path ฟอนต์ตามเครื่องคุณ)
    font = ImageFont.truetype("D:\Github\lifting-risk-assessment-system\Sarabun\Sarabun-Regular.ttf", font_size)

    # วาดข้อความ
    draw.text(position, text, font=font, fill=color)

    # แปลงกลับเป็น OpenCV
    return np.array(img_pil)
