-- File SQL dùng để khởi tạo toàn bộ bảng cho dự án: users, posts, categories, predictions.
-- ======================================
-- DATABASE INITIALIZATION FOR ML_NEWS
-- ======================================

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'editor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CATEGORIES TABLE
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- 3. POSTS TABLE
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category_id INT REFERENCES categories(id),
    image_url TEXT,
    featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. PREDICTIONS TABLE
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    feature1 REAL,
    feature2 REAL,
    feature3 REAL,
    result REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. INSERT SAMPLE CATEGORIES
INSERT INTO categories (name) VALUES
('Xã hội'),
('Môi trường'),
('Kinh tế'),
('Giáo dục')
ON CONFLICT (name) DO NOTHING;
