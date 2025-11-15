import os

# -------------------------------
# FLASK SECRET KEY
# -------------------------------
SECRET_KEY = "supersecretkey_change_this"

# -------------------------------
# DATABASE CONFIG (PostgreSQL)
# -------------------------------
DB_HOST = "localhost"
DB_NAME = "ml_news_db"
DB_USER = "postgres"
DB_PASSWORD = "your_password"   # đổi theo pgAdmin của bạn
DB_PORT = 5432

# -------------------------------
# FILE UPLOADS
# -------------------------------
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# -------------------------------
# MACHINE LEARNING MODEL PATH
# -------------------------------
MODEL_PATH = os.path.join("models", "xgb_model.pkl")
SCALER_PATH = os.path.join("models", "scaler.pkl")  # nếu bạn có scaler
