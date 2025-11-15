# File chính của dự án: Flask app.
# Chứa tất cả routes:

# CRUD bài viết

# Đăng nhập / phân quyền

# Upload ảnh

# Gọi mô hình ML

# Dashboard Chart.js
    
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
import pandas as pd
import pickle
from datetime import datetime
from functools import wraps

# -------------------------------
# Load config
# -------------------------------
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

# -------------------------------
# DB HELPER
# -------------------------------
def get_db_connection():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        port=config.DB_PORT
    )
    return conn

# -------------------------------
# UTILS
# -------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

# -------------------------------
# LOGIN REQUIRED DECORATOR
# -------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Yêu cầu quyền admin!", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapper

# -------------------------------
# LOAD MODEL
# -------------------------------
MODEL = None
if os.path.exists(config.MODEL_PATH):
    with open(config.MODEL_PATH, 'rb') as f:
        MODEL = pickle.load(f)

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        flash("Sai username hoặc password!", "danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT posts.id, posts.title, posts.created_at, categories.name as category
        FROM posts
        LEFT JOIN categories ON posts.category_id = categories.id
        ORDER BY posts.created_at DESC LIMIT 50
    """)
    posts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", posts=posts)

@app.route('/create', methods=['GET','POST'])
@login_required
def create():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM categories ORDER BY name ASC")
    categories = cur.fetchall()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')
        featured = bool(request.form.get('featured'))
        image_file = request.files.get('image')
        image_url = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(f"{datetime.utcnow().timestamp()}_{image_file.filename}")
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = url_for('uploaded_file', filename=filename)
        cur.execute("""
            INSERT INTO posts (title, content, category_id, image_url, featured, created_at)
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING id
        """, (title, content, category_id, image_url, featured, datetime.utcnow()))
        post_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        flash("Tạo bài viết thành công!", "success")
        return redirect(url_for('view', id=post_id))
    cur.close()
    conn.close()
    return render_template("create.html", categories=categories)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/view/<int:id>')
@login_required
def view(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT posts.*, categories.name as category FROM posts LEFT JOIN categories ON posts.category_id = categories.id WHERE posts.id=%s", (id,))
    post = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("view.html", post=post)

@app.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM posts WHERE id=%s", (id,))
    post = cur.fetchone()
    cur.execute("SELECT * FROM categories ORDER BY name ASC")
    categories = cur.fetchall()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')
        cur.execute("UPDATE posts SET title=%s, content=%s, category_id=%s WHERE id=%s",
                    (title, content, category_id, id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Cập nhật bài viết thành công!", "success")
        return redirect(url_for('view', id=id))
    cur.close()
    conn.close()
    return render_template("edit.html", post=post, categories=categories)

@app.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM posts WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Xóa bài viết thành công!", "success")
    return redirect(url_for('index'))

# -------------------------------
# ML PREDICT API
# -------------------------------
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if MODEL is None:
        return jsonify({"error":"Model not available"}),500
    data = request.json
    try:
        f1 = float(data.get("feature1",0))
        f2 = float(data.get("feature2",0))
        f3 = float(data.get("feature3",0))
    except:
        return jsonify({"error":"Invalid input"}),400
    df = pd.DataFrame([[f1,f2,f3]], columns=["feature1","feature2","feature3"])
    res = float(MODEL.predict(df)[0])
    # log prediction
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO predictions (feature1,feature2,feature3,result,created_at) VALUES (%s,%s,%s,%s,%s)",
                (f1,f2,f3,res,datetime.utcnow()))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"result":res})

# -------------------------------
# DASHBOARD
# -------------------------------
@app.route('/admin/dashboard')
@admin_required
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT created_at::date AS day, COUNT(*) AS count, AVG(result) AS avg_result
        FROM predictions
        GROUP BY day ORDER BY day DESC LIMIT 30
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    dates = [r['day'].strftime("%Y-%m-%d") for r in rows]
    counts = [r['count'] for r in rows]
    avgs = [float(r['avg_result']) if r['avg_result'] else 0 for r in rows]
    return render_template("dashboard.html", dates=dates, counts=counts, avgs=avgs)

# -------------------------------
# SEARCH
# -------------------------------
@app.route('/search')
@login_required
def search():
    q = request.args.get('q','')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT posts.id, posts.title, posts.created_at FROM posts WHERE title ILIKE %s OR content ILIKE %s ORDER BY created_at DESC LIMIT 50",
                (f"%{q}%", f"%{q}%"))
    posts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", posts=posts)

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
