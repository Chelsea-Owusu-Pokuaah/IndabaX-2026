--  GDSS WORKSHOP — DAY 2

--  Introduction to SQL and Relational Databases (PostgreSQL)

-- ============================================================

--  HOW TO USE THIS FILE

--  The file is divided into sections:
--    PART 1 — Database & Table Setup, Exploring the schema
--    PART 2 — Data types, constraints, NULL
--    PART 3 — SELECT, WHERE, ORDER BY, LIMIT
--    PART 4 — Module 4: DISTINCT, aliases, style
--    PART 5 — Module 5: Capstone practice

-- ============================================================

--  PART 1 — DATABASE & TABLE SETUP

-- Create the database.
-- Run this from the default 'postgres' database, then reconnect.

CREATE DATABASE shopdb;

-- ============================================================
-- Create a table.

CREATE TABLE learners (
    full_name    VARCHAR(100),
    hometown     VARCHAR(100),
    fav_tool     VARCHAR(60),
    age          INT,
    fav_color    VARCHAR(30),
    transport    VARCHAR(50),
    dream_job    VARCHAR(100)
);

-- Create a table.

INSERT INTO learners (full_name, hometown, fav_tool, age, fav_color, transport, dream_job) VALUES
    ('Ama Serwaa',        'Accra',      'Excel',         24, 'Purple',    'Trotro',       'Data Analyst'),
    ('Kwame Ofori',       'Kumasi',     'Python',        31, 'Blue',      'Motorbike',    'ML Engineer'),
    ('Abena Kyei',        'Tamale',     'PostgreSQL',    27, 'Green',     'Bicycle',      'Database Admin'),
    ('Kofi Asante',       'Accra',      'Power BI',      35, 'Black',     'Car',          'BI Developer'),
    ('Efua Mensah',       'Takoradi',   'Tableau',       22, 'Yellow',    'Walking',      'Data Journalist'),
    ('Yaw Darko',         'Accra',      'SQL',           29, 'Red',       'Uber',         'Data Engineer'),
    ('Akosua Boateng',    'Kumasi',     'R',             26, 'Orange',    'Trotro',       'Statistician'),
    ('Nana Adjei',        'Cape Coast', 'Excel',         33, 'White',     'Car',          'Product Manager'),
    ('Kojo Frimpong',     'Accra',      'Python',        28, 'Blue',      'Metro',        'AI Researcher'),
    ('Adwoa Poku',        'Tema',       'Power BI',      30, 'Pink',      'Car',          'Finance Analyst'),
    ('Fiifi Andoh',       'Accra',      'PostgreSQL',    23, 'Green',     'Walking',      'Backend Developer'),
    ('Maame Oti',         'Sunyani',    'Tableau',       38, 'Purple',    'Car',          'Policy Analyst'),
    ('Kwabena Asare',     'Accra',      'Python',        25, 'Navy',      'Bicycle',      'Data Scientist'),
    ('Adjoa Acheampong',  'Kumasi',     'SQL',           32, 'Coral',     'Trotro',       'Analytics Lead'),
    ('Bright Mensah',     'Accra',      'Excel',         21, 'Black',     'Motorbike',    'Software Developer'),
    ('Serwa Amoah',       'Ho',         'R',             27, 'Teal',      'Car',          'Research Analyst'),
    ('Emmanuel Boadu',    'Accra',      'Power BI',      34, 'Grey',      'Metro',        'Consultant'),
    ('Abigail Ofori',     'Bolgatanga', 'PostgreSQL',    26, 'Yellow',    'Bus',          'Systems Analyst'),
    ('Richmond Appiah',   'Accra',      'Python',        29, 'Blue',      'Car',          'Data Engineer'),
    ('Naana Quaye',       'Tema',       'Tableau',       31, 'Green',     'Walking',      'UX Researcher');

-- Query Table

SELECT * FROM learners;
SELECT COUNT(*) AS total_learners FROM learners;


-- Drop the table.

DROP TABLE learners;


-- ────────────────────────────────────────────────────────────
--  DATA TYPES, CONSTRAINTS & NULL

--  TABLE 1: customers
--  One row per customer. customer_id is the primary key.
--  email must be unique — no duplicate registrations.
--  country defaults to 'Ghana' if not supplied.
-- ────────────────────────────────────────────────────────────
CREATE TABLE customers (
    customer_id   SERIAL       PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,
    city          VARCHAR(60),
    country       VARCHAR(60)  NOT NULL DEFAULT 'Ghana',
    joined_date   DATE         NOT NULL
);

INSERT INTO customers (first_name, last_name, email, city, country, joined_date) VALUES
    ('Ama',      'Owusu',     'ama@mail.com',      'Accra',    'Ghana', '2022-03-14'),
    ('Kwame',    'Mensah',    'kwame@mail.com',    'Kumasi',   'Ghana', '2021-11-05'),
    ('Abena',    'Asante',    'abena@mail.com',    'Accra',    'Ghana', '2023-01-20'),
    ('Kofi',     'Boateng',   'kofi@mail.com',     'Tamale',   'Ghana', '2022-07-30'),
    ('Efua',     'Darko',     'efua@mail.com',     'Accra',    'Ghana', '2023-06-11'),
    ('Yaw',      'Acheampong','yaw@mail.com',      'Kumasi',   'Ghana', '2020-09-01'),
    ('Akosua',   'Frimpong',  'akosua@mail.com',   'Takoradi', 'Ghana', '2023-08-22'),
    ('Nana',     'Adjei',     'nana@mail.com',     'Accra',    'Ghana', '2021-04-17');


-- ────────────────────────────────────────────────────────────
--  TABLE 2: products
--  One row per product.
--  price uses DECIMAL(10,2) — exact precision for money.
--  is_active = FALSE means the product has been discontinued.
-- ────────────────────────────────────────────────────────────
CREATE TABLE products (
    product_id   SERIAL        PRIMARY KEY,
    product_name VARCHAR(100)  NOT NULL,
    category     VARCHAR(50)   NOT NULL,
    price        DECIMAL(10,2) NOT NULL,
    stock_qty    INT           NOT NULL DEFAULT 0,
    is_active    BOOLEAN       NOT NULL DEFAULT TRUE
);

INSERT INTO products (product_name, category, price, stock_qty, is_active) VALUES
    ('Wireless Headphones Pro', 'Electronics', 149.99,  80,  TRUE),
    ('Laptop Stand Aluminium',  'Accessories',  45.00, 200,  TRUE),
    ('USB-C Hub 7-Port',        'Electronics',  62.50, 150,  TRUE),
    ('Mechanical Keyboard',     'Electronics', 110.00,  60,  TRUE),
    ('Desk Lamp LED',           'Accessories',  28.00, 300,  TRUE),
    ('Webcam 1080p',            'Electronics',  75.00,  90,  TRUE),
    ('Cable Management Kit',    'Accessories',  15.00, 400,  TRUE),
    ('Portable SSD 1TB',        'Electronics', 120.00,  45, FALSE),
    ('Ergonomic Mouse',         'Accessories',  55.00, 110,  TRUE),
    ('Monitor Arm Dual',        'Furniture',   135.00,  30,  TRUE);


-- ────────────────────────────────────────────────────────────
--  TABLE 3: orders
--  One row per order.
--  customer_id is a foreign key → customers(customer_id).
--  total_amount is nullable: an order may not be priced yet.
--  status defaults to 'pending'.
-- ────────────────────────────────────────────────────────────
CREATE TABLE orders (
    order_id     SERIAL        PRIMARY KEY,
    customer_id  INT           NOT NULL REFERENCES customers(customer_id),
    order_date   DATE          NOT NULL,
    status       VARCHAR(20)   NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) 
);

INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES
    (1, '2024-01-10', 'delivered',  194.99),
    (1, '2024-03-05', 'delivered',   45.00),
    (2, '2024-02-14', 'delivered',  172.50),
    (3, '2024-03-20', 'shipped',    110.00),
    (4, '2024-04-01', 'pending',     28.00),
    (5, '2024-04-03', 'cancelled',   75.00),
    (6, '2024-01-28', 'delivered',  349.99),
    (7, '2024-02-09', 'delivered',   55.00),
    (8, '2024-03-30', 'shipped',    135.00),
    (2, '2024-04-05', 'pending',     62.50),
    (3, '2024-04-06', 'pending',    120.00),
    (1, '2023-12-20', 'delivered',   75.00);


-- ────────────────────────────────────────────────────────────
--  TABLE 4: order_items
--  One row per product line within an order.
--  Links orders ↔ products (the many-to-many junction table).
--  quantity must be > 0 — enforced by a CHECK constraint.
-- ────────────────────────────────────────────────────────────
CREATE TABLE order_items (
    item_id    SERIAL        PRIMARY KEY,
    order_id   INT           NOT NULL REFERENCES orders(order_id),
    product_id INT           NOT NULL REFERENCES products(product_id),
    quantity   INT           NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL
);
 
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    ( 1,  1, 1, 149.99),
    ( 1,  2, 1,  45.00),
    ( 2,  2, 1,  45.00),
    ( 3,  3, 1,  62.50),
    ( 3,  9, 2,  55.00),
    ( 4,  4, 1, 110.00),
    ( 5,  5, 1,  28.00),
    ( 6,  6, 1,  75.00),
    ( 7,  1, 1, 149.99),
    ( 7,  3, 1,  62.50),
    ( 7,  4, 1, 110.00),
    ( 7,  7, 2,  15.00),
    ( 8,  9, 1,  55.00),
    ( 9, 10, 1, 135.00),
    (10,  3, 1,  62.50),
    (11,  8, 1, 120.00),
    (12,  6, 1,  75.00);


-- ============================================================
--  RELATIONAL DATABASES & DATA ORGANISATION

--  Learning goal: understand how the tables relate,
-- ============================================================

-- ── Look at every table to understand the data ──────────────

SELECT * FROM customers;
SELECT * FROM products;
SELECT * FROM orders;
SELECT * FROM order_items;


-- ── List all tables in the current database ─────────────────

SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type   = 'BASE TABLE'
ORDER BY table_name;
 
 
-- ── Inspect a table's columns, types, and constraints ───────
-- Change the table_name value to inspect any other table.

SELECT
    column_name,
    data_type,
    character_maximum_length  AS max_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name   = 'customers'
  AND table_schema = 'public'
ORDER BY ordinal_position;
 
-- Run the same query for each table by changing table_name:
-- WHERE table_name = 'orders'
-- WHERE table_name = 'products'
-- WHERE table_name = 'order_items'


-- ============================================================
--  DATA TYPES, CONSTRAINTS & NULL

--  Learning goal: understand what lives in each column,
--  why types matter, and how NULL is different from zero.
-- ============================================================

-- ── Numeric types in products ───────────────────────────────

-- DECIMAL(10,2): up to 10 digits total, exactly 2 decimal places.
-- INT: whole numbers only — stock_qty cannot be 2.5.

SELECT
    column_name,
    data_type,
    numeric_precision,
    numeric_scale
FROM information_schema.columns
WHERE table_name   = 'products'
  AND table_schema = 'public';


-- ── Date arithmetic: only works because order_date is DATE ──
-- If order_date were VARCHAR this subtraction would fail.

SELECT
    order_id,
    order_date,
    CURRENT_DATE                  AS today,
    CURRENT_DATE - order_date     AS days_since_order
FROM orders
ORDER BY order_date DESC;


-- ── NULL is not zero ─────────────────────────────────────────

-- total_amount is nullable. A NULL means the amount is unknown,
-- not that the order is free (which would be 0.00).


-- Correct way to find NULL values:

SELECT order_id, status, total_amount
FROM orders
WHERE total_amount IS NULL;


-- Correct way to find non-NULL values:

SELECT order_id, status, total_amount
FROM orders
WHERE total_amount IS NOT NULL;


-- ── Constraints in action ────────────────────────────────────

-- Try inserting an order for a customer who does not exist.
-- The foreign key constraint will reject it.

INSERT INTO orders (customer_id, order_date, status)
VALUES (999, '2024-04-10', 'pending');

--Expected: ERROR: insert or update on table "orders" violates


-- Try inserting a zero-quantity line item.

-- The CHECK constraint will reject it.

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES (1, 1, 0, 149.99);

-- Expected: ERROR: new row for relation "order_items"


-- ── Exercise 2: Schema reading ───────────────────────────────

-- Run this query for order_items, then answer the questions below.
--   1. Why is unit_price DECIMAL rather than FLOAT?
--   2. What is the CHECK constraint on quantity, and why does it make sense?
--   3. What happens if you insert an order_id that does not exist in orders?
--   4. Is item_id nullable? How can you tell?

SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name   = 'order_items'
  AND table_schema = 'public'
ORDER BY ordinal_position;


-- ============================================================
--  SELECT, WHERE, ORDER BY, LIMIT

--  Learning goal: read data from a single table using
--  filters, sorting, and result size controls.
-- ============================================================

-- ── Basic SELECT ─────────────────────────────────────────────

-- All columns, all rows
SELECT * FROM customers;


-- Specific columns only
SELECT first_name, last_name, city
FROM customers;


-- Limit to a safe preview on any large table
SELECT * FROM orders LIMIT 5;


-- ── WHERE — filtering rows ───────────────────────────────────

-- Equality
SELECT first_name, last_name, city
FROM customers
WHERE city = 'Accra';

-- Greater / less than
SELECT name, price
FROM products
WHERE price > 100;

SELECT name, price
FROM products
WHERE price <= 50;

-- Not equal (both syntaxes are valid)
SELECT order_id, status
FROM orders
WHERE status != 'delivered';
-- WHERE status <> 'delivered';  -- same result


-- ── AND / OR / NOT ───────────────────────────────────────────

-- Both conditions must be true
SELECT order_id, customer_id, order_date, status
FROM orders
WHERE status    = 'pending'
  AND order_date >= '2024-04-01';

-- Either condition can be true
SELECT first_name, city
FROM customers
WHERE city = 'Accra'
   OR city = 'Kumasi';

-- NOT inverts a condition
SELECT name, category
FROM products
WHERE NOT category = 'Electronics';


-- ── Parentheses matter with AND + OR ─────────────────────────

-- Query A: returns delivered orders from customer 1,
--          PLUS all orders from customer 2 (any status)
SELECT order_id, customer_id, status
FROM orders
WHERE status = 'delivered'
  AND customer_id = 1
   OR customer_id = 2;

-- Query B: returns delivered orders for customer 1 or 2 only
SELECT order_id, customer_id, status
FROM orders
WHERE status = 'delivered'
  AND (customer_id = 1 OR customer_id = 2);

-- Compare the row counts — they differ!
-- Always use parentheses when mixing AND and OR.


-- ── NULL filtering ───────────────────────────────────────────
SELECT order_id, status, total_amount
FROM orders
WHERE total_amount IS NULL;

SELECT order_id, status, total_amount
FROM orders
WHERE total_amount IS NOT NULL;


-- ── LIKE and ILIKE — pattern matching ───────────────────────

-- % matches any sequence of characters (including none)
-- _ matches exactly one character

-- Case-sensitive (LIKE)
SELECT name, category
FROM products
WHERE name LIKE '%Pro%';

-- Case-insensitive (ILIKE — PostgreSQL specific)
SELECT name, category
FROM products
WHERE name ILIKE '%pro%';

-- Starts with
SELECT name FROM products WHERE name LIKE 'Wireless%';

-- Any name containing 'Hub'
SELECT name FROM products WHERE name ILIKE '%hub%';


-- ── IN and BETWEEN ───────────────────────────────────────────

-- IN: cleaner than multiple OR conditions
SELECT order_id, status
FROM orders
WHERE status IN ('pending', 'shipped');

-- BETWEEN: inclusive on both ends
SELECT name, price
FROM products
WHERE price BETWEEN 50 AND 130;

-- BETWEEN with dates
SELECT first_name, joined_date
FROM customers
WHERE joined_date BETWEEN '2022-01-01' AND '2022-12-31';


-- ── ORDER BY ─────────────────────────────────────────────────

-- Ascending (default — ASC can be omitted)
SELECT name, price
FROM products
ORDER BY price ASC;

-- Descending
SELECT name, price
FROM products
ORDER BY price DESC;

-- Multi-column sort: city A→Z, then newest joiners first within each city
SELECT first_name, city, joined_date
FROM customers
ORDER BY city ASC, joined_date DESC;


-- ── LIMIT and OFFSET ─────────────────────────────────────────

-- Top 3 most expensive products
SELECT name, price
FROM products
ORDER BY price DESC
LIMIT 3;

-- Next 3 (rows 4–6) — pagination pattern
SELECT name, price
FROM products
ORDER BY price DESC
LIMIT 3 OFFSET 3;


-- ── Exercise 3: Writing WHERE, ORDER BY, LIMIT ───────────────
-- Write these queries. All answers come from one table.

-- 1. All Electronics products, sorted by price descending.
SELECT name, price
FROM products
WHERE category = 'Electronics'
ORDER BY price DESC;

-- 2. Orders placed on or after 1 March 2024 that are not cancelled.
SELECT order_id, order_date, status
FROM orders
WHERE order_date >= '2024-03-01'
  AND status != 'cancelled';

-- 3. The 3 most expensive active products with stock.
SELECT name, price
FROM products
WHERE stock_qty > 0
  AND is_active = TRUE
ORDER BY price DESC
LIMIT 3;

-- 4. Customers whose email contains 'mail.com'.
SELECT first_name, email
FROM customers
WHERE email ILIKE '%mail.com%';

-- 5. STRETCH: Orders with total_amount between 50 and 150, cheapest first.
SELECT order_id, total_amount
FROM orders
WHERE total_amount BETWEEN 50 AND 150
ORDER BY total_amount ASC;


-- ============================================================
--  DISTINCT, ALIASES & QUERY STYLE

--  Learning goal: write clean, readable SQL;
--  remove duplicates; rename output columns and tables.
-- ============================================================

-- ── Query style: bad vs good ─────────────────────────────────

-- Hard to read (valid SQL, but avoid this in real work)
SELECT name,price,stock_qty FROM products WHERE is_active=true AND category='Electronics' ORDER BY price DESC LIMIT 5;

-- Same query — well-formatted
-- Top 5 active Electronics products by price
SELECT
    name,
    price,
    stock_qty
FROM products
WHERE is_active  = TRUE
  AND category   = 'Electronics'
ORDER BY price DESC
LIMIT 5;


-- ── Comments ─────────────────────────────────────────────────

-- Single-line comment: use -- before the text

/*
   Multi-line comment: use /* and */
   Use these to describe a complex query at the top.
*/


-- ── DISTINCT — unique values only ────────────────────────────

-- Without DISTINCT: one row per customer (cities repeat)
SELECT city
FROM customers
ORDER BY city;

-- With DISTINCT: each city appears once
SELECT DISTINCT city
FROM customers
ORDER BY city;

-- Distinct combinations of two columns
SELECT DISTINCT category, is_active
FROM products
ORDER BY category;

-- Practical use: what statuses exist in our orders?
SELECT DISTINCT status
FROM orders
ORDER BY status;


-- ── Column aliases with AS ───────────────────────────────────

-- Rename columns for readable output
SELECT
    first_name    AS "First Name",
    last_name     AS "Last Name",
    city          AS "City",
    joined_date   AS "Member Since"
FROM customers
ORDER BY joined_date;

-- Calculated column with alias
SELECT
    name                          AS "Product",
    price                         AS "Price (GHS)",
    price * 0.8                   AS "Discounted Price",
    stock_qty                     AS "Units Available"
FROM products
WHERE is_active = TRUE;


-- ── Table aliases ────────────────────────────────────────────

-- Shortening table names — especially useful in multi-table queries.
-- 'c' is now a shorthand for 'customers'.
-- 'o' is a shorthand for 'orders'.
-- (Full JOIN syntax is covered in Day 2 — this is a preview.)
SELECT
    c.first_name,
    c.city,
    o.order_date,
    o.status
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.city = 'Accra';


-- ── Alias scoping: SELECT aliases are NOT available in WHERE ─

-- This fails — 'discounted_price' does not exist when WHERE runs:
-- SELECT price * 0.8 AS discounted_price
-- FROM products
-- WHERE discounted_price < 50;    -- ERROR

-- Correct: repeat the expression in WHERE
SELECT
    name,
    price * 0.8 AS discounted_price
FROM products
WHERE price * 0.8 < 50;


-- ── Exercise 4: Style, DISTINCT & aliases ────────────────────
-- Rewrite this messy query with proper style and aliases:
-- select product_id,name,price,stock_qty from products
-- where is_active=true and category='Electronics' order by price desc limit 5;

-- Answer:
-- Top 5 active Electronics products, formatted and aliased
SELECT
    product_id    AS "ID",
    name          AS "Product Name",
    price         AS "Price (GHS)",
    stock_qty     AS "Units in Stock"
FROM products
WHERE is_active  = TRUE
  AND category   = 'Electronics'
ORDER BY price DESC
LIMIT 5;

-- Find all distinct order statuses, aliased:
SELECT DISTINCT status AS "Order Status"
FROM orders
ORDER BY "Order Status";

-- Why does this fail, and how do you fix it?
-- SELECT price * 1.15 AS price_with_tax
-- FROM products
-- WHERE price_with_tax > 100;
--
-- Answer: WHERE runs before SELECT, so the alias doesn't exist yet.
-- Fix:
SELECT
    name,
    price * 1.15 AS price_with_tax
FROM products
WHERE price * 1.15 > 100;


============================================================
--  PART 6 — MODULE 5: AGGREGATION
--  Learning goal: summarise data using GROUP BY, COUNT, SUM,
--  AVG, MIN, MAX and filter grouped results with HAVING.
--
--  Timing: ~20 minutes (fits by trimming the SQL flavours
--  comparison table from Module 4 — that content is reference
--  material learners can read independently)
-- ============================================================
 
-- ── Why aggregation? ─────────────────────────────────────────
-- SELECT returns one row per record.
-- Aggregation collapses multiple rows into a single summary value.
-- This is the foundation of every dashboard, report, and KPI.
 
 
-- ── COUNT ────────────────────────────────────────────────────
 
-- How many rows are in the table?
SELECT COUNT(*) AS total_orders
FROM orders;
 
-- COUNT(*) counts all rows including NULLs.
-- COUNT(column) counts only non-NULL values in that column.
SELECT
    COUNT(*)             AS total_orders,
    COUNT(total_amount)  AS orders_with_amount
FROM orders;
-- If these numbers differ, some rows have NULL in total_amount.
 
-- Count with a filter — how many orders were delivered?
SELECT COUNT(*) AS delivered_orders
FROM orders
WHERE status = 'delivered';
 
 
-- ── SUM and AVG ──────────────────────────────────────────────
 
-- Total revenue from all delivered orders
SELECT SUM(total_amount) AS total_revenue
FROM orders
WHERE status = 'delivered';
 
-- Average order value across all completed (non-pending) orders
SELECT ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
WHERE status != 'pending';
 
 
-- ── MIN and MAX ──────────────────────────────────────────────
 
SELECT
    MIN(price)  AS cheapest_product,
    MAX(price)  AS most_expensive_product,
    AVG(price)  AS average_price
FROM products
WHERE is_active = TRUE;
 
 
-- ── GROUP BY — aggregating per group ─────────────────────────
-- Without GROUP BY, aggregates collapse the entire table to one row.
-- GROUP BY splits the table into groups first, then aggregates each group.
 
-- How many orders does each status have?
SELECT
    status,
    COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY order_count DESC;
 
-- Total stock quantity and average price per category
SELECT
    category,
    COUNT(*)                    AS product_count,
    SUM(stock_qty)              AS total_stock,
    ROUND(AVG(price), 2)        AS avg_price,
    MIN(price)                  AS min_price,
    MAX(price)                  AS max_price
FROM products
GROUP BY category
ORDER BY category;
 
-- How many customers joined per year?
SELECT
    EXTRACT(YEAR FROM joined_date)  AS join_year,
    COUNT(*)                        AS new_customers
FROM customers
GROUP BY EXTRACT(YEAR FROM joined_date)
ORDER BY join_year;
 
 
-- ── A common GROUP BY mistake ────────────────────────────────
-- Every column in SELECT must either be in GROUP BY
-- or wrapped in an aggregate function.
-- This FAILS — name is not aggregated or grouped:
--
-- SELECT category, name, COUNT(*)
-- FROM products
-- GROUP BY category;
-- ERROR: column "products.name" must appear in the GROUP BY clause
--        or be used in an aggregate function
 
 
-- ── HAVING — filtering on aggregated results ─────────────────
-- WHERE filters individual rows BEFORE grouping.
-- HAVING filters groups AFTER aggregation.
 
-- Which categories have more than 3 products?
SELECT
    category,
    COUNT(*) AS product_count
FROM products
GROUP BY category
HAVING COUNT(*) > 3;
 
-- Which order statuses have a total value above 200 GHS?
SELECT
    status,
    COUNT(*)                    AS order_count,
    ROUND(SUM(total_amount), 2) AS total_value
FROM orders
GROUP BY status
HAVING SUM(total_amount) > 200
ORDER BY total_value DESC;
 
-- WHERE vs HAVING used together:
-- Filter rows first with WHERE, then filter groups with HAVING.
-- Orders placed in 2024 only: which statuses have more than 1 order?
SELECT
    status,
    COUNT(*) AS order_count
FROM orders
WHERE order_date >= '2024-01-01'     -- WHERE: filters individual rows first
GROUP BY status
HAVING COUNT(*) > 1                  -- HAVING: filters groups after aggregation
ORDER BY order_count DESC;
 
 
-- ── Exercise 5: Aggregation ──────────────────────────────────
-- Write each query yourself before checking the answer.
 
-- Q1. How many products are there in each category?
--     Show category and product count. Sort by count descending.
SELECT
    category,
    COUNT(*) AS product_count
FROM products
GROUP BY category
ORDER BY product_count DESC;
 
-- Q2. What is the total value of stock on hand per category?
--     (Total value = price * stock_qty for each product, summed per category.)
--     Show only active products. Sort by total value descending.
SELECT
    category,
    ROUND(SUM(price * stock_qty), 2)  AS total_stock_value
FROM products
WHERE is_active = TRUE
GROUP BY category
ORDER BY total_stock_value DESC;
 
-- Q3. How many orders has each customer placed?
--     Show customer_id and order count.
--     Only show customers with more than 1 order.
SELECT
    customer_id,
    COUNT(*)  AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY order_count DESC;
 
-- Q4. What is the average total_amount for each order status?
--     Round to 2 decimal places. Exclude NULL amounts.
--     (Hint: COUNT(*) vs COUNT(column) — which handles NULLs correctly here?)
SELECT
    status,
    COUNT(total_amount)              AS counted_orders,  -- skips NULLs
    ROUND(AVG(total_amount), 2)      AS avg_order_value
FROM orders
GROUP BY status
ORDER BY avg_order_value DESC;
 
-- Q5. STRETCH: Find categories where the average product price
--     is above 60 GHS. Show category and average price (rounded).
--     Only include active products in the calculation.
SELECT
    category,
    ROUND(AVG(price), 2)  AS avg_price
FROM products
WHERE is_active = TRUE
GROUP BY category
HAVING AVG(price) > 60
ORDER BY avg_price DESC;
 
 
-- ============================================================
--  PART 7 — MODULE 6: CAPSTONE PRACTICE
-- ============================================================
 
-- ── Challenge 1 ──────────────────────────────────────────────
-- The operations team wants a status summary for all orders
-- placed in 2024. For each status, show:
--   - the number of orders (as "Order Count")
--   - the total value (as "Total Value (GHS)", rounded to 2dp)
--   - the average value (as "Avg Value (GHS)", rounded to 2dp)
-- Sort by Total Value descending.
-- Exclude any status group where the total value is below 50 GHS.
 
SELECT
    status                              AS "Status",
    COUNT(*)                            AS "Order Count",
    ROUND(SUM(total_amount),  2)        AS "Total Value (GHS)",
    ROUND(AVG(total_amount),  2)        AS "Avg Value (GHS)"
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY status
HAVING SUM(total_amount) >= 50
ORDER BY SUM(total_amount) DESC;
 
 
-- ── Challenge 2 ──────────────────────────────────────────────
-- The buying team wants to review the active product catalogue.
-- For each category, show:
--   - number of active products
--   - cheapest and most expensive active product price
--   - total units in stock
-- Only show categories that have at least 2 active products.
-- Sort alphabetically by category.
 
SELECT
    category                            AS "Category",
    COUNT(*)                            AS "Active Products",
    MIN(price)                          AS "Lowest Price (GHS)",
    MAX(price)                          AS "Highest Price (GHS)",
    SUM(stock_qty)                      AS "Total Units in Stock"
FROM products
WHERE is_active = TRUE
GROUP BY category
HAVING COUNT(*) >= 2
ORDER BY category;
 
 
-- ── Challenge 3 ──────────────────────────────────────────────
-- Find all products that are:
--   - active
--   - priced above the average price of ALL active products
-- Show name, category, and price.
-- Sort by price descending.
-- Hint: you will need a subquery in WHERE to get the average first.
 
SELECT
    name,
    category,
    price
FROM products
WHERE is_active = TRUE
  AND price > (
        SELECT AVG(price)
        FROM products
        WHERE is_active = TRUE
      )
ORDER BY price DESC;
 
 
-- ── Challenge 4 ──────────────────────────────────────────────
-- A report needs to show each city alongside:
--   - the number of customers based there
--   - the earliest join date (as "First Member Joined")
--   - the most recent join date (as "Latest Member Joined")
-- Only include cities with more than 1 customer.
-- Sort by customer count descending.
 
SELECT
    city                                    AS "City",
    COUNT(*)                                AS "Customers",
    MIN(joined_date)                        AS "First Member Joined",
    MAX(joined_date)                        AS "Latest Member Joined"
FROM customers
GROUP BY city
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;
 
 
-- ── Challenge 5 (STRETCH) ────────────────────────────────────
-- The finance team wants to identify high-value pending business.
-- Find all pending orders where total_amount is above the average
-- total_amount of ALL non-cancelled orders.
-- Show order_id, customer_id, order_date, and total_amount.
-- Sort by total_amount descending.
 
SELECT
    order_id,
    customer_id,
    order_date,
    total_amount
FROM orders
WHERE status       = 'pending'
  AND total_amount > (
        SELECT AVG(total_amount)
        FROM orders
        WHERE status != 'cancelled'
      )
ORDER BY total_amount DESC;
 


-- ============================================================
--  END OF FILE
-- ============================================================
