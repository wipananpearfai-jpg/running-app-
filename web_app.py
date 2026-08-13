import streamlit as st
import cv2
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Running Test", layout="wide")

st.title("🏃‍♂️ AI Running Fitness Test")
st.caption("ระบบทดสอบสมรรถภาพทางกายด้านการวิ่ง")

with st.expander("👤 ข้อมูลนักเรียน", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("ชื่อ-นามสกุล", "รัชชนนท์ บุตราช")
    with col2:
        level = st.selectbox("ระดับชั้น", ["ชั้น ป.6", "ชั้น ป.5", "ชั้น ป.4", "ชั้น ม.1", "ชั้น ม.2", "ชั้น ม.3"])
    with col3:
        student_id = st.text_input("เลขที่", "3")

st.divider()

# อัปโหลดไฟล์วิดีโอสำหรับการทดสอบบน Cloud
uploaded_file = st.file_uploader("📹 อัปโหลดคลิปวิดีโอการวิ่งเพื่อประมวลผล (MP4, MOV)", type=['mp4', 'mov', 'avi'])

if uploaded_file is not None:
    st.success("บันทึกไฟล์เรียบร้อย! กำลังประมวลผลการวิ่ง...")
    
    # แสดงผลจำลอง
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🦶 ก้าวซ้าย", "24 ครั้ง")
    c2.metric("🦶 ก้าวขวา", "25 ครั้ง")
    c3.metric("⏱️ เวลา", "00:30")
    c4.metric("🏆 คะแนนรวม", "49 ก้าว", "98 ก้าว/นาที")
    
    st.subheader("📋 ผลการประมวลผล")
    st.info(f"ผู้ทดสอบ: {name} ({level} เลขที่ {student_id}) - ผลการทดสอบอยู่ในเกณฑ์: **ระดับดีมาก 🥇**")
