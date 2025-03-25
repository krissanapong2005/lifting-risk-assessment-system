import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
import cv2
import os
import mediapipe as mp
import csv
import numpy as np

from lifting_assessment import assess_lifting_risk, draw_thai_text
from pose_utils import detect_twist_angle
from sector import table_values  # ฟังก์ชันใหม่

# === ตั้งค่า Mediapipe Pose Drawing ===
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# === ฟังก์ชันหลักที่ประมวลผลวิดีโอ ===
def run_analysis(weight_str, freq_str):
    try:
        actual_weight = float(weight_str)
        lifting_freq_option = int(freq_str)
    except ValueError:
        messagebox.showerror("Invalid Input", "กรุณากรอกตัวเลขให้ถูกต้อง")
        return

    cap = cv2.VideoCapture(r'D:\Github\lifting-risk-assessment-system\video_ยกของ.mp4')
    if not cap.isOpened():
        messagebox.showerror("Video Error", "ไม่สามารถเปิดไฟล์วิดีโอได้")
        return

    os.makedirs('output', exist_ok=True)

    csv_path = 'output/analysis_results.csv'
    try:
        csv_file = open(csv_path, mode='w', newline='', encoding='utf-8-sig')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Frame', 'LH Index', 'Risk Level', 'Twist Angle', 'RWL', 'Position'])

        pose = mp_pose.Pose(static_image_mode=False)
        frame_idx = 0

        while cap.isOpened():
            for _ in range(3):  # ข้ามบางเฟรมเพื่อเร่งความเร็ว
                ret, frame = cap.read()
                if not ret:
                    break

            frame_idx += 1
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results and results.pose_landmarks:
                landmarks = results.pose_landmarks
                h, w = frame.shape[0], frame.shape[1]

                # เตรียม keypoints สำหรับ table_values
                def xy(landmark_enum):  # รับ enum ตรง ๆ เช่น mp_pose.PoseLandmark.LEFT_ANKLE
                    lm = landmarks.landmark[landmark_enum]
                    return [lm.x * w, lm.y * h]  # คืน [x, y] พิกเซล

                foot = xy(mp_pose.PoseLandmark.LEFT_FOOT_INDEX)
                heel = xy(mp_pose.PoseLandmark.LEFT_HEEL)
                shoulder = xy(mp_pose.PoseLandmark.LEFT_SHOULDER)
                hip = xy(mp_pose.PoseLandmark.LEFT_HIP)
                knee = xy(mp_pose.PoseLandmark.LEFT_KNEE)
                hand = xy(mp_pose.PoseLandmark.LEFT_WRIST)

                # 1. หาตำแหน่งและโซน
                position, sector = table_values(foot, heel, shoulder, hip, knee, hand, w, h, landmarks)

                # เช็กว่า table_values คืนค่า None ไหม
                if position is None or sector is None:
                    print(f"⚠️ Frame {frame_idx}: ไม่สามารถระบุตำแหน่งมือได้ ข้ามเฟรมนี้")
                    continue
                    
                position_text = f"{position} / {sector}"

                # 2. ตรวจการบิดตัว
                twist_angle, is_twisted = detect_twist_angle(landmarks)

                # 3. ประเมินความเสี่ยง
                result = assess_lifting_risk(
                    position=position,
                    sector=sector,
                    actual_weight=actual_weight,
                    lifting_freq_option=lifting_freq_option,
                    is_twisted=is_twisted
                )

                # 4. วาดผลบนภาพ
                annotated = frame.copy()
                mp_drawing.draw_landmarks(
                    annotated,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=3),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 128, 255), thickness=2)
                )

                cv2.putText(annotated, f"LH Index: {result['lh_index']:.2f} (Level {result['risk_level_num']})", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                cv2.putText(annotated, f"Twist Angle: {twist_angle:.1f} deg", (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                cv2.putText(annotated, f"RWL: {result['rwl']:.2f} kg", (30, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                thai_text = f"ตำแหน่ง: {position_text}"
                annotated = draw_thai_text(annotated, thai_text, position=(30, 140), font_size=28, color=(0, 0, 0))

                # บันทึกภาพและผล
                cv2.imwrite(f'output/frame_{frame_idx}.jpg', annotated)

                csv_writer.writerow([
                    frame_idx,
                    f"{result['lh_index']:.2f}",
                    result['risk_level'],
                    f"{twist_angle:.1f}",
                    f"{result['rwl']:.2f}",
                    position_text
                ])

        cap.release()
        csv_file.close()
        messagebox.showinfo("เสร็จสิ้น", "วิเคราะห์สำเร็จ! ไปดูผลได้ในโฟลเดอร์ output")

    except Exception as e:
        messagebox.showerror("CSV Error", f"เกิดข้อผิดพลาด: {e}")

    finally:
        if 'csv_file' in locals() and not csv_file.closed:
            csv_file.close()

# === GUI ===
root = tk.Tk()
root.title("LiftGuard - Lifting Risk Assessment")
root.geometry("400x250")

tk.Label(root, text="น้ำหนักที่ยกจริง (kg):").pack(pady=(20, 5))
entry_weight = tk.Entry(root)
entry_weight.pack()

tk.Label(root, text="จำนวนรอบการยก:").pack(pady=(15, 5))
combo_freq = ttk.Combobox(root, state="readonly")
combo_freq['values'] = [
    "1 - ยก 1 ครั้งทุก 2-5 นาที",
    "2 - ยก 2-3 ครั้ง/นาที",
    "3 - ยกมากกว่า 10 ครั้ง/นาที"
]
combo_freq.current(1)
combo_freq.pack()

def on_run():
    weight = entry_weight.get()
    freq_option = combo_freq.get().split(" ")[0]
    threading.Thread(target=run_analysis, args=(weight, freq_option), daemon=True).start()

tk.Button(root, text="Run Analysis", command=on_run, bg="green", fg="white").pack(pady=20)
root.mainloop()
