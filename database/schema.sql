-- ====================================================================
-- Customer Segmentation and Predictive Analytics System
-- Relational Database Schema (MySQL)
-- Strictly defines ONLY the 5 required entities per specification.
-- ====================================================================

CREATE DATABASE IF NOT EXISTS customer_segmentation_db;
USE customer_segmentation_db;

-- 1. Table: customers
DROP TABLE IF EXISTS customer_segments;
DROP TABLE IF EXISTS segment_runs;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INT NOT NULL,
    customer_code VARCHAR(50) NOT NULL,
    signup_date DATE NULL,
    PRIMARY KEY (customer_id),
    UNIQUE KEY uq_customer_code (customer_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Table: orders
CREATE TABLE orders (
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Table: order_items
CREATE TABLE order_items (
    item_id INT AUTO_INCREMENT NOT NULL,
    order_id INT NOT NULL,
    product_identifier VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (item_id),
    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders (order_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Table: segment_runs
CREATE TABLE segment_runs (
    run_id INT AUTO_INCREMENT NOT NULL,
    method VARCHAR(50) NOT NULL,
    run_date DATETIME NOT NULL,
    parameters TEXT NULL,
    PRIMARY KEY (run_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Table: customer_segments
CREATE TABLE customer_segments (
    run_id INT NOT NULL,
    customer_id INT NOT NULL,
    segment_label VARCHAR(100) NOT NULL,
    PRIMARY KEY (run_id, customer_id),
    CONSTRAINT fk_cust_seg_run
        FOREIGN KEY (run_id) REFERENCES segment_runs (run_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cust_seg_customer
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
