-- Create database (run manually or via psql)
-- CREATE DATABASE inventory_db;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(100),   -- plaintext [VULN]
    role VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    description TEXT,
    quantity INTEGER,
    price NUMERIC(10, 2)
);

-- Seed users (plaintext passwords) [VULN]
INSERT INTO users (username, password, role, email) VALUES
('admin',  'admin123',    'admin', 'admin@corp.local'),
('sysadmin','sysadmin!',  'admin', 'sysadmin@corp.local'),
('alice',  'password1',   'user',  'alice@corp.local'),
('bob',    'password2',   'user',  'bob@corp.local'),
('charlie','password3',   'user',  'charlie@corp.local');

-- Seed inventory items
INSERT INTO inventory (name, description, quantity, price) VALUES
('Laptop',        'Dell XPS 15 — 16GB RAM',        12,  1299.99),
('Monitor',       'LG 27" 4K Display',             8,   499.99),
('Keyboard',      'Mechanical RGB Keyboard',        25,  89.99),
('Mouse',         'Logitech MX Master 3',          30,  99.99),
('Webcam',        'Logitech C920 HD Pro',          15,  79.99),
('Headset',       'Sony WH-1000XM5',              10,  349.99),
('USB Hub',       '7-Port USB 3.0 Hub',           40,  39.99),
('Desk Lamp',     'LED Smart Desk Lamp',           20,  49.99),
('Cable Mgmt',    'Cable management tray set',     50,  19.99),
('Server Rack',   '12U Open Frame Rack',           3,   299.99);
