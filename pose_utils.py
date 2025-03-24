import numpy as np
import mediapipe as mp

def get_vector(p1, p2):
    return np.array([p2.x - p1.x, p2.y - p1.y])

def get_angle_between(v1, v2):
    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    return np.degrees(np.arccos(cos_theta))

def detect_twist_angle(landmarks):
    ls = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    rs = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
    lh = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP]
    rh = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

    shoulder_vec = get_vector(ls, rs)
    hip_vec = get_vector(lh, rh)

    angle = get_angle_between(shoulder_vec, hip_vec)
    return angle, angle > 45

def get_hand_position_info(landmarks):
    # เฉลี่ยมือซ้าย/ขวา ถ้ามีทั้งคู่
    lh = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
    rh = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]
    mid_hand_x = (lh.x + rh.x) / 2
    mid_hand_y = (lh.y + rh.y) / 2

    # ความสูงแนวตั้ง (y): 0 = top, 1 = bottom → เทียบกับสะโพกและไหล่
    hip_y = (landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP].y +
             landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP].y) / 2
    shoulder_y = (landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y +
                  landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].y) / 2

    height_level = 'เอวถึงหัวเข่า'
    if mid_hand_y < shoulder_y:
        height_level = 'เหนือหัวไหล่'
    elif mid_hand_y > hip_y:
        height_level = 'ใต้เอว'

    # ระยะแนวนอน (x): 0 = ซ้ายสุด, 1 = ขวาสุด → ประมาณว่าใกล้ตัว/กลาง/ไกล
    rel_x = abs(mid_hand_x - 0.5)
    if rel_x < 0.1:
        dist = 'ใกล้ตัว'
    elif rel_x < 0.2:
        dist = 'ปานกลาง'
    else:
        dist = 'เหยียดแขน'

    return {'height': height_level, 'distance': dist}