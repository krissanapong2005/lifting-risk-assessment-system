def assess_lifting_risk(position, sector, actual_weight, lifting_freq_option, is_twisted):
    # ตาราง RWL จากตำแหน่งและระยะ (ภาษาอังกฤษ)
    table = {
        ('Over Shoulder', 'Sector1'): 29,
        ('Over Shoulder', 'Sector2'): 24,
        ('Over Shoulder', 'Sector3'): 18,

        ('Between Shoulder and Hip', 'Sector1'): 32,
        ('Between Shoulder and Hip', 'Sector2'): 33,
        ('Between Shoulder and Hip', 'Sector3'): 25,

        ('Between Hip and Knee', 'Sector1'): 41,
        ('Between Hip and Knee', 'Sector2'): 25,
        ('Between Hip and Knee', 'Sector3'): 18,

        ('Lower Knee', 'Sector1'): 31,
        ('Lower Knee', 'Sector2'): 23,
        ('Lower Knee', 'Sector3'): 16
    }

    base_rwl = table.get((position, sector), 10)
    freq_multiplier = {1: 1.0, 2: 0.75, 3: 0.6}.get(lifting_freq_option, 1.0)
    twist_multiplier = 0.85 if is_twisted else 1.0

    rwl = base_rwl * freq_multiplier * twist_multiplier
    lh_index = (actual_weight / rwl) * 100 if rwl > 0 else 999

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

# === วาดข้อความภาษาไทยด้วยฟอนต์ Sarabun ===
from PIL import ImageFont, ImageDraw, Image
import numpy as np

def draw_thai_text(image, text, position, font_size=28, color=(255, 255, 255)):
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)

    font = ImageFont.truetype("D:/Github/lifting-risk-assessment-system/Sarabun/Sarabun-Regular.ttf", font_size)
    draw.text(position, text, font=font, fill=color)

    return np.array(img_pil)
