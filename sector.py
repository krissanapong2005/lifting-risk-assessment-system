import numpy as np
import mediapipe as mp


def table_values(foot, heel, shoulder, hip, knee, hand, width, height, landmarks):
    # คำนวณระยะระหว่างเท้ากับส้นเท้า
    distance_vector = np.array(foot) - np.array(heel)
    distance = np.linalg.norm(distance_vector) * 1.5  # ขยายระยะให้ใหญ่ขึ้น

    # คำนวณจุดแบ่งโซน (Sector) โดยใช้ค่า x
    sector1 = np.array(foot) + [distance, 0]
    sector2 = sector1 + [distance, 0]
    sector3 = sector2 + [distance, 0]

    # คำนวณตำแหน่งมือ (ต้องแปลงเป็นพิกเซล)
    lh = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
    rh = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]
    mid_hand_x = ((lh.x + rh.x) / 2) * width
    mid_hand_y = ((lh.y + rh.y) / 2) * height

    # คำนวณตำแหน่งแนวแกน Y ของไหล่, สะโพก, เข่า (แปลงเป็นพิกเซล)
    shoulder_y = ((landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y +
                   landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].y) / 2) * height
    hip_y = ((landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP].y +
              landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP].y) / 2) * height
    knee_y = ((landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE].y +
               landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_KNEE].y) / 2) * height

    # ตรวจสอบว่าอยู่ในโซนไหน
    if mid_hand_x < sector1[0]:  
        sector = "Sector1"
    elif sector1[0] <= mid_hand_x < sector2[0]:
        sector = "Sector2"
    elif sector2[0] <= mid_hand_x < sector3[0]:
        sector = "Sector3"
    else:
        return None, None  # ✅ เปลี่ยนตรงนี้ (คืน 2 ค่าเสมอ!)

    # ตรวจสอบตำแหน่งแนวแกน Y
    if mid_hand_y < shoulder_y:
        position = "Over Shoulder"
    elif mid_hand_y < hip_y:
        position = "Between Shoulder and Hip"
    elif mid_hand_y < knee_y:
        position = "Between Hip and Knee"
    else:
        position = "Lower Knee"

    return position, sector