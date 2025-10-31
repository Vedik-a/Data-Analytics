create database retail;
show tables;
table brands;
table categories;
table customers;
table order_items;
table orders;
table products;
table staffs;
table stocks;
table stores;
SHOW COLUMNS FROM stocks;
SHOW COLUMNS FROM stores;
SHOW COLUMNS FROM brands;
SHOW COLUMNS FROM categories;
SHOW COLUMNS FROM customers;
SHOW COLUMNS FROM order_items;
SHOW COLUMNS FROM orders;
SHOW COLUMNS FROM staffs;
SHOW COLUMNS FROM products;


SELECT * FROM brands LIMIT 10;
SELECT * FROM stores LIMIT 10;
SELECT * FROM stocks LIMIT 10;

-- Join stock store and brand tables
SELECT 
    s.store_name,
    s.city,
    b.brand_name,
    st.quantity
FROM stocks st
JOIN stores s ON st.store_id = s.store_id
JOIN brands b ON st.product_id = b.brand_id;

-- State-wise total stock value
SELECT 
    s.state,
    SUM(st.quantity) AS total_stock
FROM stocks st
JOIN stores s ON st.store_id = s.store_id
GROUP BY s.state
ORDER BY total_stock DESC;

-- Average Discount Given
SELECT 
  ROUND(AVG(discount) * 100, 2) AS avg_discount_percent
FROM order_items;

-- Count by State
SELECT state, COUNT(*) AS total_customers
FROM customers
GROUP BY state
ORDER BY total_customers DESC;

-- Cities with Most Customers
SELECT city, COUNT(*) AS total_customers
FROM customers
GROUP BY city
ORDER BY total_customers DESC
LIMIT 10;

-- Orders by Month
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    COUNT(order_id) AS total_orders
FROM orders
GROUP BY month
ORDER BY month;

-- Orders per Staff
SELECT 
    s.staff_id,
    CONCAT(s.first_name, ' ', s.last_name) AS staff_name,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN staffs s ON o.staff_id = s.staff_id
GROUP BY s.staff_id, s.first_name, s.last_name
ORDER BY total_orders DESC;

-- Active vs Inactive Staff
SELECT 
    active,
    COUNT(*) AS total_staff
FROM staffs
GROUP BY active;

-- highest priced product
SELECT 
    product_id,
    product_name,
    list_price
FROM products
ORDER BY list_price DESC
LIMIT 10;