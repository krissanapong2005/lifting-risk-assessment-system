import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
import cv2
import os
import mediapipe as mp
import csv
from lifting_assessment import assess_lifting_risk
from pose_utils import get_hand_position_info, detect_twist_angle


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def run_analysis(weight_str, freq_str):
    try:
        actual_weight = float(weight_str)
        lifting_freq_option = int(freq_str)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid number values.")
        return

    cap = cv2.VideoCapture(r'D:\Github\lifting-risk-assessment-system\video_ยกของ.mp4')
    if not cap.isOpened():
        messagebox.showerror("Video Error", "ไม่สามารถเปิดไฟล์ video.mp4 ได้")
        return

    os.makedirs('output', exist_ok=True)

    csv_path = 'output/analysis_results.csv'
    try:
        csv_file = open(csv_path, mode='w', newline='', encoding='utf-8-sig')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Frame', 'LH Index', 'Risk Level', 'Twist Angle', 'RWL'])

        pose = mp_pose.Pose(static_image_mode=False)

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results and results.pose_landmarks:
                hand_info = get_hand_position_info(results.pose_landmarks)
                twist_angle, is_twisted = detect_twist_angle(results.pose_landmarks)

                result = assess_lifting_risk(
                    hand_info=hand_info,
                    actual_weight=actual_weight,
                    lifting_freq_option=lifting_freq_option,
                    is_twisted=is_twisted
                )

                annotated = frame.copy()


                mp_drawing.draw_landmarks(
                    annotated,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=3),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 128, 255), thickness=2)
                )


                cv2.putText(annotated, f"LH Index: {result['lh_index']:.2f} (Level {result['risk_level'].split()[1]})", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(annotated, f"Twist Angle: {twist_angle:.1f} deg", (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(annotated, f"RWL: {result['rwl']:.2f} kg", (30, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                cv2.imwrite(f'output/frame_{frame_idx}.jpg', annotated)

                csv_writer.writerow([
                    frame_idx,
                    f"{result['lh_index']:.2f}",
                    result['risk_level'],
                    f"{twist_angle:.1f}",
                    f"{result['rwl']:.2f}"
                ])

        cap.release()
        csv_file.close()
        messagebox.showinfo("เสร็จสิ้น", "การวิเคราะห์เสร็จแล้ว! ไปดูผลลัพธ์ในโฟลเดอร์ output ได้เลย")
    except Exception as e:
        messagebox.showerror("CSV Error", f"เกิดข้อผิดพลาดในการเขียนไฟล์ CSV: {e}")
    finally:
        if 'csv_file' in locals() and not csv_file.closed:
            csv_file.close()


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

# ปุ่มรัน
def on_run():
    weight = entry_weight.get()
    freq_option = combo_freq.get().split(" ")[0]
    threading.Thread(target=run_analysis, args=(weight, freq_option), daemon=True).start()

tk.Button(root, text="Run Analysis", command=on_run, bg="green", fg="white").pack(pady=20)

root.mainloop()