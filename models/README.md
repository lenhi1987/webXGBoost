Hướng dẫn lưu trữ mô hình ML.
# Mô hình ML cho ML News Platform

## 1. XGBoost Model
- File: `xgb_model.pkl`
- Đặt trong thư mục `models/`
- Sử dụng để dự đoán giá trị từ feature1, feature2, feature3.

## 2. Scaler (nếu có)
- File: `scaler.pkl`
- Dùng để chuẩn hóa dữ liệu trước khi dự đoán.
- Tùy chọn: nếu mô hình đã tích hợp scaler, không cần file này.

## 3. Cách tạo mô hình mới
```python
import pickle
from xgboost import XGBRegressor
import pandas as pd

# ví dụ data
X = pd.DataFrame([[1,2,3],[4,5,6]], columns=['feature1','feature2','feature3'])
y = [10, 20]

model = XGBRegressor()
model.fit(X, y)

# lưu model
with open('models/xgb_model.pkl', 'wb') as f:
    pickle.dump(model, f)
