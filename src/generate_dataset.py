"""
Dataset generator for Customer Segmentation Project.
Generates realistic, anonymized transaction data.
"""
import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_sample_data(output_path: str, seed: int = 42):
    np.random.seed(seed)
    random.seed(seed)

    # Categories and realistic products with unit prices
    products = [
        {"id": "PROD-001", "name": "Wireless Ergonomic Mouse", "price": 29.99},
        {"id": "PROD-002", "name": "Mechanical Gaming Keyboard", "price": 89.50},
        {"id": "PROD-003", "name": "Ultra HD 27-inch Monitor", "price": 289.00},
        {"id": "PROD-004", "name": "Noise Cancelling Headphones", "price": 149.99},
        {"id": "PROD-005", "name": "USB-C Multi-Port Docking Station", "price": 59.99},
        {"id": "PROD-006", "name": "Smart Fitness Fitness Tracker", "price": 49.95},
        {"id": "PROD-007", "name": "Anker 65W Fast Charger", "price": 35.00},
        {"id": "PROD-008", "name": "Laptop Aluminum Stand", "price": 24.50},
        {"id": "PROD-009", "name": "1TB External Solid State Drive", "price": 109.99},
        {"id": "PROD-010", "name": "Webcam 1080p HD with Microphone", "price": 45.00},
        {"id": "PROD-011", "name": "Desk Mat Extended Gaming Pad", "price": 18.50},
        {"id": "PROD-012", "name": "Ergonomic Mesh Office Chair", "price": 320.00},
    ]

    base_date = datetime(2024, 6, 30)  # Snapshot reference anchor
    records = []
    order_id_counter = 10001

    # We curate customer archetypes to ensure clear, realistic RFM segments exist
    customer_archetypes = (
        [("Champions", 25)] +
        [("Loyal", 30)] +
        [("BigSpenders", 15)] +
        [("NewCustomers", 25)] +
        [("AtRisk", 25)] +
        [("Lost", 30)]
    )

    cust_id = 1
    for archetype, count in customer_archetypes:
        for _ in range(count):
            customer_code = f"CUST-{cust_id:04d}"
            
            if archetype == "Champions":
                num_orders = random.randint(6, 12)
                recency_days = random.randint(2, 25)
                avg_items = random.randint(2, 5)
                price_bias = "high"
            elif archetype == "Loyal":
                num_orders = random.randint(4, 7)
                recency_days = random.randint(20, 65)
                avg_items = random.randint(1, 3)
                price_bias = "medium"
            elif archetype == "BigSpenders":
                num_orders = random.randint(1, 3)
                recency_days = random.randint(10, 80)
                avg_items = random.randint(2, 4)
                price_bias = "very_high"
            elif archetype == "NewCustomers":
                num_orders = random.randint(1, 2)
                recency_days = random.randint(2, 40)
                avg_items = random.randint(1, 2)
                price_bias = "medium"
            elif archetype == "AtRisk":
                num_orders = random.randint(4, 8)
                recency_days = random.randint(120, 240)
                avg_items = random.randint(1, 3)
                price_bias = "medium"
            else:  # Lost
                num_orders = random.randint(1, 2)
                recency_days = random.randint(250, 480)
                avg_items = random.randint(1, 2)
                price_bias = "low"

            latest_date = base_date - timedelta(days=recency_days, hours=random.randint(1, 12))
            
            order_dates = [latest_date]
            for _ in range(num_orders - 1):
                prior_offset = random.randint(20, 100)
                prior_date = order_dates[-1] - timedelta(days=prior_offset, hours=random.randint(1, 10))
                order_dates.append(prior_date)

            order_dates.sort()

            for o_date in order_dates:
                order_id = order_id_counter
                order_id_counter += 1

                # Realistic status: mostly Completed/Delivered, small portion Cancelled/Refunded
                status_roll = random.random()
                if status_roll < 0.88:
                    order_status = "Completed"
                elif status_roll < 0.95:
                    order_status = "Delivered"
                elif status_roll < 0.98:
                    order_status = "Cancelled"
                else:
                    order_status = "Refunded"

                num_items = max(1, int(np.random.poisson(avg_items)))
                if price_bias == "very_high":
                    prod_candidates = [p for p in products if p["price"] >= 100.0]
                elif price_bias == "high":
                    prod_candidates = products
                elif price_bias == "medium":
                    prod_candidates = [p for p in products if p["price"] <= 150.0]
                else:
                    prod_candidates = [p for p in products if p["price"] <= 60.0]

                selected_prods = random.choices(prod_candidates, k=num_items)
                for prod in selected_prods:
                    qty = random.randint(1, 3) if price_bias != "very_high" else random.randint(1, 2)
                    records.append({
                        "order_id": order_id,
                        "customer_id": cust_id,
                        "customer_code": customer_code,
                        "order_date": o_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "order_status": order_status,
                        "product_id": prod["id"],
                        "product_name": prod["name"],
                        "quantity": qty,
                        "unit_price": prod["price"]
                    })

            cust_id += 1

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated sample dataset with {len(df)} rows across {df['customer_id'].nunique()} customers at {output_path}")

if __name__ == "__main__":
    generate_sample_data("data/customer_purchase_data.csv")
