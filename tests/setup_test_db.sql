-- tests/setup_test_db.sql

-- Drop tables if they exist
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Create products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    category_id INT REFERENCES categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    order_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert test data
INSERT INTO users (name, email, age) VALUES
    ('Alice Smith', 'alice@example.com', 28),
    ('Bob Johnson', 'bob@example.com', 35),
    ('Charlie Brown', 'charlie@example.com', 42),
    ('Diana Ross', 'diana@example.com', 31),
    ('Edward Norton', 'edward@example.com', 45);

INSERT INTO categories (name, description) VALUES
    ('Electronics', 'Electronic devices and accessories'),
    ('Books', 'Physical and digital books'),
    ('Clothing', 'Apparel and fashion items'),
    ('Home & Garden', 'Items for home improvement and gardening');

INSERT INTO products (name, description, price, stock, category_id) VALUES
    ('Smartphone', 'High-end smartphone with advanced features', 699.99, 50, 1),
    ('Laptop', 'Powerful laptop for work and gaming', 1299.99, 30, 1),
    ('Classic Novel', 'Timeless literary masterpiece', 15.99, 100, 2),
    ('T-shirt', 'Comfortable cotton t-shirt', 19.99, 200, 3),
    ('Garden Tools Set', 'Essential tools for gardening', 49.99, 40, 4),
    ('Wireless Earbuds', 'True wireless earbuds with noise cancellation', 159.99, 75, 1),
    ('Cookbook', 'Collection of gourmet recipes', 24.99, 60, 2),
    ('Jeans', 'Durable denim jeans', 39.99, 150, 3),
    ('Indoor Plant', 'Low-maintenance indoor plant', 29.99, 80, 4);

INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES
    (1, 1, 1, 699.99),
    (1, 3, 2, 31.98),
    (2, 2, 1, 1299.99),
    (3, 4, 3, 59.97),
    (3, 5, 1, 49.99),
    (4, 6, 1, 159.99),
    (4, 7, 1, 24.99),
    (5, 8, 2, 79.98),
    (5, 9, 3, 89.97),
    (2, 1, 1, 699.99);