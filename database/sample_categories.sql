-- File SQL thêm danh mục mẫu (nếu muốn reset hoặc thêm mới).
-- Thêm danh mục mẫu
INSERT INTO categories (name) VALUES
('Xã hội'),
('Môi trường'),
('Kinh tế'),
('Giáo dục'),
('Y tế'),
('Công nghệ')
ON CONFLICT (name) DO NOTHING;
