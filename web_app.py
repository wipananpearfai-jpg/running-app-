import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="AI Running Test", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; }
    .score-card { background-color: #1f2937; padding: 20px; border-radius: 12px; text-align: center; border: 2px solid #3b82f6; }
    </style>
""", unsafe_allow_html=True)

if 'test_finished' not in st.session_state:
    st.session_state.test_finished = False

st.title("🏃‍♂️ AI Running Fitness Test")
st.caption("ระบบทดสอบสมรรถภาพทางกายด้านการวิ่งด้วย AI")

if not st.session_state.test_finished:
    with st.expander("👤 ข้อมูลนักเรียน", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input("ชื่อ-นามสกุล", "รัชชนนท์ บุตราช")
        with col2:
            level = st.selectbox("ระดับชั้น", ["ชั้น ป.6", "ชั้น ป.5", "ชั้น ป.4", "ชั้น ม.1", "ชั้น ม.2", "ชั้น ม.3"])
        with col3:
            student_id = st.text_input("เลขที่", "3")
        with col4:
            test_duration = st.selectbox("เวลาทดสอบ (วินาที)", [30, 60, 120], index=0)

    start_btn = st.button("▶️ เริ่มทดสอบการวิ่ง", use_container_width=True, type="primary")

    if start_btn:
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        m_left = c1.empty()
        m_right = c2.empty()
        m_time = c3.empty()
        m_total = c4.empty()

        camera_place = st.empty()

        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            model_complexity=0,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        left_steps = 0
        right_steps = 0
        left_state = False
        right_state = False
        start_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            elapsed = int(time.time() - start_time)
            remaining_time = max(0, test_duration - elapsed)

            frame = cv2.resize(frame, (480, 360))
            h, w, _ = frame.shape
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            results = pose.process(image)

            ground_y = int(h * 0.75)
            cv2.line(image, (0, ground_y), (w, ground_y), (0, 255, 128), 2)
            cv2.putText(image, "Ground Line", (15, ground_y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 128), 1)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                left_foot = int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * h)
                right_foot = int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y * h)

                cv2.circle(image, (int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * w), left_foot), 8, (255, 0, 0), -1)
                cv2.circle(image, (int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * w), right_foot), 8, (0, 255, 0), -1)

                if left_foot < ground_y - 20 and not left_state:
                    left_steps += 1
                    left_state = True
                elif left_foot >= ground_y - 5:
                    left_state = False

                if right_foot < ground_y - 20 and not right_state:
                    right_steps += 1
                    right_state = True
                elif right_foot >= ground_y - 5:
                    right_state = False

            total_steps = left_steps + right_steps

            m_left.metric("🦶 ก้าวซ้าย", f"{left_steps}")
            m_right.metric("🦶 ก้าวขวา", f"{right_steps}")
            m_time.metric("⏱️ เวลาคงเหลือ", f"00:{remaining_time:02d}")
            m_total.metric("🏆 ก้าวรวม (คะแนน)", f"{total_steps}", f"{(total_steps/(max(1, elapsed))*60):.0f} ก้าว/นาที")

            camera_place.image(image, channels="RGB", use_container_width=True)
            time.sleep(0.01)

            if remaining_time <= 0:
                st.session_state.user_name = name
                st.session_state.level = level
                st.session_state.student_id = student_id
                st.session_state.duration = test_duration
                st.session_state.left_steps = left_steps
                st.session_state.right_steps = right_steps
                st.session_state.total_steps = total_steps
                st.session_state.cadence = int((total_steps / test_duration) * 60)
                st.session_state.test_finished = True
                cap.release()
                st.rerun()

else:
    st.button("🔄 ทดสอบใหม่อีกครั้ง", on_click=lambda: st.session_state.update({"test_finished": False}))
    
    st.header("📋 ผลการทดสอบสมรรถภาพ")
    
    total = st.session_state.total_steps
    if total >= 40:
        level_text = "ระดับดีมาก 🥇"
        sub_text = "คุณมีความเร็วและความคล่องตัวสูงมาก"
        score_num = 95
    elif total >= 25:
        level_text = "ระดับปานกลาง 🥈"
        sub_text = "ทำได้ดี พยายามฝึกฝนความสม่ำเสมอเพิ่มอีกนิด"
        score_num = 75
    else:
        level_text = "ระดับ ควรฝึกเพิ่มเติม ⚠️"
        sub_text = "พยายามเข้า คุณทำได้ดีกว่านี้!"
        score_num = 46

    r1, r2 = st.columns([1, 2])
    with r1:
        st.markdown(f"""
        <div class="score-card">
            <h2>คะแนนรวม</h2>
            <h1 style="font-size: 60px; color: #60a5fa;">{score_num}</h1>
            <h3>{level_text}</h3>
            <p style="color: #9ca3af;">{sub_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with r2:
        st.subheader(f"ผู้ทดสอบ: {st.session_state.user_name} ({st.session_state.level} เลขที่ {st.session_state.student_id})")
        
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("ก้าวซ้าย", f"{st.session_state.left_steps} ครั้ง")
        sc2.metric("ก้าวขวา", f"{st.session_state.right_steps} ครั้ง")
        sc3.metric("ความถี่ (Cadence)", f"{st.session_state.cadence} ก้าว/นาที")

        st.subheader("📊 กราฟสรุปดัชนีการทดสอบ")
        chart_data = pd.DataFrame({
            "รายการ": ["ก้าวซ้าย", "ก้าวขวา", "ก้าวรวม", "ความถี่ (ก้าว/นาที)"],
            "จำนวน": [st.session_state.left_steps, st.session_state.right_steps, st.session_state.total_steps, st.session_state.cadence]
        })
        st.bar_chart(chart_data.set_index("รายการ"))
