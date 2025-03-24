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
    # ดึงตำแหน่งข้อมือและหัวไหล่
    lh = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
    rh = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]
    ls = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    rs = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
    lhip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP]
    rhip = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP]
    lknee = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE]
    rknee = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_KNEE]

    # จุดกลางของมือและหัวไหล่
    mid_hand_x = (lh.x + rh.x) / 2
    mid_hand_y = (lh.y + rh.y) / 2
    mid_shoulder_x = (ls.x + rs.x) / 2
    mid_shoulder_y = (ls.y + rs.y) / 2

    # คำนวณระยะห่างจากหัวไหล่ในแนวนอน
    dist_x = abs(mid_hand_x - mid_shoulder_x)

    # Normalize ระยะห่างเทียบกับช่วงไหล่
    shoulder_width = abs(ls.x - rs.x)
    rel_dist = dist_x / shoulder_width if shoulder_width > 0 else 0

    # แบ่งระยะห่างจากลำตัว (อิงกับไหล่)
    if rel_dist < 0.4:
        distance = 'ใกล้ตัว'
    elif rel_dist < 0.8:
        distance = 'ปานกลาง'
    else:
        distance = 'เหยียดแขน'

    # ประเมินระดับความสูง
    hip_y = (lhip.y + rhip.y) / 2
    knee_y = (lknee.y + rknee.y) / 2
    shoulder_y = mid_shoulder_y

    if mid_hand_y < shoulder_y:
        height = 'เหนือหัวไหล่'
    elif mid_hand_y < hip_y:
        height = 'หัวไหล่ถึงเอว'
    elif mid_hand_y < knee_y:
        height = 'เอวถึงหัวเข่า'
    else:
        height = 'ใต้เข่า'

    return {'height': height, 'distance': distance}