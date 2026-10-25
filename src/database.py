"""
Database Module for MySQL Integration.
Handles database connection, schema initialization, raw data loading,
and recording segmentation runs strictly adhering to the schema specification.
"""

import os
import json
from typing import Optional, Dict, Any
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Default MySQL configuration parameters (customizable via env or arguments)
DEFAULT_DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "customer_segmentation_db"),
}

def get_db_connection(config: Optional[Dict[str, Any]] = None, with_database: bool = True):
    """
    Establishes a MySQL database connection.
    Returns the connection object if successful, or None if connection fails.
    """
    cfg = config or DEFAULT_DB_CONFIG
    conn_params = {
        "host": cfg.get("host", "localhost"),
        "port": cfg.get("port", 3306),
        "user": cfg.get("user", "root"),
        "password": cfg.get("password", "")
    }
    if with_database:
        conn_params["database"] = cfg.get("database", "customer_segmentation_db")

    try:
        connection = mysql.connector.connect(**conn_params)
        return connection
    except Error as e:
        return None

def test_mysql_connection(config: Optional[Dict[str, Any]] = None) -> bool:
    """Checks whether MySQL server is reachable."""
    conn = get_db_connection(config, with_database=False)
    if conn and conn.is_connected():
        conn.close()
        return True
    return False

def initialize_database(schema_path: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Initializes the database schema using database/schema.sql.
    """
    cfg = config or DEFAULT_DB_CONFIG
    conn = get_db_connection(cfg, with_database=False)
    if not conn:
        print("[DATABASE] MySQL connection not established. Skipping database schema initialization.")
        return False

    try:
        cursor = conn.cursor()
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Execute statements sequentially
        statements = sql_script.split(";")
        for stmt in statements:
            cleaned_stmt = stmt.strip()
            if cleaned_stmt:
                cursor.execute(cleaned_stmt)
        conn.commit()
        cursor.close()
        conn.close()
        print("[DATABASE] MySQL schema initialized successfully.")
        return True
    except Error as e:
        print(f"[DATABASE] Error initializing schema: {e}")
        if conn and conn.is_connected():
            conn.close()
        return False

def store_raw_data_to_mysql(df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Stores customers, orders, and order_items into MySQL tables.
    """
    conn = get_db_connection(config, with_database=True)
    if not conn:
        print("[DATABASE] MySQL not available. Raw data will be processed from CSV.")
        return False

    try:
        cursor = conn.cursor()

        # 1. Populate 'customers'
        # Group by customer_id and customer_code, signup_date derived from first order date
        cust_df = (
            df.groupby(["customer_id", "customer_code"])["order_date"]
            .min()
            .reset_index()
        )
        cust_df["signup_date"] = pd.to_datetime(cust_df["order_date"]).dt.date

        cust_sql = """
            INSERT INTO customers (customer_id, customer_code, signup_date)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE customer_code=VALUES(customer_code)
        """
        cust_records = [
            (int(row["customer_id"]), str(row["customer_code"]), row["signup_date"])
            for _, row in cust_df.iterrows()
        ]
        cursor.executemany(cust_sql, cust_records)

        # 2. Populate 'orders'
        # Unique orders
        orders_df = (
            df[["order_id", "customer_id", "order_date", "order_status"]]
            .drop_duplicates(subset=["order_id"])
        )
        orders_sql = """
            INSERT INTO orders (order_id, customer_id, order_date, order_status)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE order_status=VALUES(order_status)
        """
        order_records = [
            (
                int(row["order_id"]),
                int(row["customer_id"]),
                pd.to_datetime(row["order_date"]).strftime("%Y-%m-%d %H:%M:%S"),
                str(row["order_status"])
            )
            for _, row in orders_df.iterrows()
        ]
        cursor.executemany(orders_sql, order_records)

        # 3. Populate 'order_items'
        # Clear existing items if any to avoid duplicates on re-run
        cursor.execute("DELETE FROM order_items")
        items_sql = """
            INSERT INTO order_items (order_id, product_identifier, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """
        item_records = [
            (
                int(row["order_id"]),
                str(row["product_id"]),
                int(row["quantity"]),
                float(row["unit_price"])
            )
            for _, row in df.iterrows()
        ]
        cursor.executemany(items_sql, item_records)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DATABASE] Successfully inserted {len(cust_records)} customers, {len(order_records)} orders, and {len(item_records)} order_items.")
        return True
    except Error as e:
        print(f"[DATABASE] Error inserting transaction data: {e}")
        if conn and conn.is_connected():
            conn.close()
        return False

def record_segmentation_run(
    method: str,
    parameters: dict,
    segment_series: pd.Series,
    config: Optional[Dict[str, Any]] = None
) -> Optional[int]:
    """
    Records a segmentation execution in 'segment_runs' and per-customer labels in 'customer_segments'.
    """
    conn = get_db_connection(config, with_database=True)
    if not conn:
        print(f"[DATABASE] MySQL not connected. Skipping DB persistence for run '{method}'.")
        return None

    try:
        cursor = conn.cursor()
        run_sql = """
            INSERT INTO segment_runs (method, run_date, parameters)
            VALUES (%s, NOW(), %s)
        """
        cursor.execute(run_sql, (method, json.dumps(parameters)))
        run_id = cursor.lastrowid

        seg_sql = """
            INSERT INTO customer_segments (run_id, customer_id, segment_label)
            VALUES (%s, %s, %s)
        """
        seg_records = [
            (run_id, int(cust_id), str(label))
            for cust_id, label in segment_series.items()
        ]
        cursor.executemany(seg_sql, seg_records)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DATABASE] Recorded run #{run_id} ({method}) with {len(seg_records)} customer segments into MySQL.")
        return run_id
    except Error as e:
        print(f"[DATABASE] Error recording segmentation run: {e}")
        if conn and conn.is_connected():
            conn.close()
        return None
