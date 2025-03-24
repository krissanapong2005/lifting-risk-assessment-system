def assess_lifting_risk(hand_info, actual_weight, lifting_freq_option, is_twisted):
    # ตาราง RWL น้ำหนักพื้นฐานตามตำแหน่ง
    table = {
        ('เหนือหัวไหล่', 'ใกล้ตัว'): 14,
        ('เหนือหัวไหล่', 'ปานกลาง'): 18,
        ('เหนือหัวไหล่', 'เหยียดแขน'): 29,
        ('เอวถึงหัวเข่า', 'ใกล้ตัว'): 23,
        ('เอวถึงหัวเข่า', 'ปานกลาง'): 32,
        ('เอวถึงหัวเข่า', 'เหยียดแขน'): 35,
        ('ใต้เอว', 'ใกล้ตัว'): 21,
        ('ใต้เอว', 'ปานกลาง'): 26,
        ('ใต้เอว', 'เหยียดแขน'): 41
    }
    base_rwl = table.get((hand_info['height'], hand_info['distance']), 10)

    # ตัวคูณจากจำนวนรอบการยก (สมมุติค่าตามแบบประเมิน)
    freq_multiplier = {1: 1.0, 2: 0.75, 3: 0.6}.get(lifting_freq_option, 1.0)
    twist_multiplier = 0.85 if is_twisted else 1.0

    rwl = base_rwl * freq_multiplier * twist_multiplier
    lh_index = (actual_weight / rwl) * 100 if rwl > 0 else 999

    # ประเมินระดับความเสี่ยง
    if lh_index < 50:
        level = 'ระดับ 1 (ยกได้ปลอดภัย)'
    elif lh_index < 75:
        level = 'ระดับ 2 (ควรตรวจสอบ)'
    elif lh_index <= 100:
        level = 'ระดับ 3 (เริ่มเสี่ยง)'
    else:
        level = 'ระดับ 4 (อันตรายสูง)'

    return {
        'rwl': rwl,
        'lh_index': lh_index,
        'risk_level': level
    }