import streamlit as st
import joblib
import numpy as np

# Load mô hình XGBoost
model = joblib.load("src/saved_models/XGBoost.pkl")

# Tiêu đề trang
st.set_page_config(page_title="XGBoost Predictor", page_icon="🌿", layout="centered")
st.title("🌿 Ứng dụng Dự đoán với XGBoost")
st.write("Nhập các giá trị đầu vào để mô hình dự đoán kết quả:")

# Ví dụ: mô hình có 3 đặc trưng
col1, col2, col3 = st.columns(3)
with col1:
    f1 = st.number_input("Feature 1", value=0.0)
with col2:
    f2 = st.number_input("Feature 2", value=0.0)
with col3:
    f3 = st.number_input("Feature 3", value=0.0)

# Nút dự đoán
if st.button("🔮 Dự đoán"):
    X = np.array([[f1, f2, f3]])
    prediction = model.predict(X)[0]
    st.success(f"Kết quả dự đoán: **{prediction:.3f}**")