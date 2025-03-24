import numpy as np
import mediapipe as mp

# === ฟังก์ชันช่วย: สร้างเวกเตอร์จาก landmark 2 จุด ===
def get_vector(p1, p2):
    # คืนเวกเตอร์ 2D [x, y] จากจุด p1 ไป p2
    return np.array([p2.x - p1.x, p2.y - p1.y])

# === ฟังก์ชันช่วย: คำนวณมุมระหว่างเวกเตอร์ 2 เส้น (unit: องศา) ===
def get_angle_between(v1, v2):
    # dot product หารด้วยผลคูณของ norm
    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    # ป้องกันเลขล้นขอบเกิน ±1
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    # คืนค่ามุม (degree)
    return np.degrees(np.arccos(cos_theta))

# === ฟังก์ชันหลัก: ตรวจสอบว่าลำตัวบิดหรือไม่ ===
def detect_twist_angle(landmarks):
    # ดึงตำแหน่งไหล่ซ้าย-ขวา และสะโพกซ้าย-ขวา
    ls = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    rs = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
    lh = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP]
    rh = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

    # สร้างเวกเตอร์จากไหล่ซ้ายไปขวา และสะโพกซ้ายไปขวา
    shoulder_vec = get_vector(ls, rs)
    hip_vec = get_vector(lh, rh)

    # คำนวณมุมระหว่างไหล่กับสะโพก (ถ้าตรง = 0°, ถ้าบิด = มุมมากขึ้น)
    angle = get_angle_between(shoulder_vec, hip_vec)

    # คืนค่า: มุม, และ boolean ว่าบิดตัวเกิน 45° หรือไม่
    return angle, angle > 45

# === ฟังก์ชันหลัก: วิเคราะห์ตำแหน่งมือ (ระดับความสูง + ระยะจากลำตัว) ===
def get_hand_position_info(landmarks):
    # ดึงตำแหน่งข้อมือซ้ายและขวา แล้วหาค่ากลาง (midpoint)
    lh = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
    rh = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]
    mid_hand_x = (lh.x + rh.x) / 2
    mid_hand_y = (lh.y + rh.y) / 2

    # ดึงค่าระดับอ้างอิงสำหรับการแบ่งระดับความสูง
    shoulder_y = (landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y +
                  landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].y) / 2
    hip_y = (landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP].y +
             landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP].y) / 2
    knee_y = (landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE].y +
              landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_KNEE].y) / 2

    # แบ่งความสูงของมือเป็น 4 ช่วง ตามแบบฟอร์ม
    if mid_hand_y < shoulder_y:
        height_level = 'เหนือหัวไหล่'
    elif mid_hand_y < hip_y:
        height_level = 'หัวไหล่ถึงเอว'
    elif mid_hand_y < knee_y:
        height_level = 'หัวเข่าถึงเอว'
    else:
        height_level = 'ใต้เข่า'

    # วิเคราะห์ "ระยะห่างจากลำตัว" จากระยะห่างในแนวนอนจากจุดกลางภาพ (0.5)
    rel_x = abs(mid_hand_x - 0.5)
    if rel_x < 0.1:
        dist = 'ใกล้ตัว'
    elif rel_x < 0.2:
        dist = 'ปานกลาง'
    else:
        dist = 'เหยียดแขน'

    # คืนผลลัพธ์เป็น dictionary
    return {'height': height_level, 'distance': dist}
