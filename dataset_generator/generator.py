import numpy as np
import pandas as pd

def generate_events(n, users, products, orders, rng):
    user_ids = users["user_id"].to_numpy()
    product_ids = products["product_id"].to_numpy()

    # Popular products receive disproportionately more interactions.
    pweights = np.exp(-np.arange(len(product_ids)) / 11)
    pweights /= pweights.sum()

    rows = []
    event_probs = [0.48, 0.25, 0.10, 0.07, 0.04, 0.04, 0.02]
    for eid in range(1, n + 1):
        uid = int(rng.choice(user_ids))
        event_type = str(rng.choice(
            ["page_view", "product_view", "search", "add_to_cart", "wishlist", "checkout", "purchase"],
            p=event_probs
        ))
        pid = None
        query = None
        if event_type in {"product_view", "add_to_cart", "wishlist", "purchase"}:
            pid = int(rng.choice(product_ids, p=pweights))
        elif event_type == "search":
            query = str(rng.choice([
                "wireless headphones", "running shoes", "python book", "gaming keyboard",
                "office chair", "skin care", "fitness tracker", "coffee maker"
            ]))
        event_date = pd.Timestamp(rng.choice(pd.date_range("2024-01-01", "2026-08-31", freq="D")))
        timestamp = event_date + pd.Timedelta(seconds=int(rng.integers(0, 86400)))
        rows.append({
            "event_id": eid,
            "user_id": uid,
            "event_type": event_type,
            "product_id": pid,
            "search_query": query,
            "event_timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return pd.DataFrame(rows)
import numpy as np
import pandas as pd

def generate_orders(n, users, products, rng, start_date, end_date):
    user_ids = users["user_id"].to_numpy()
    # Heterogeneous customer activity: a smaller group buys much more often.
    weights = np.array([1.0] * len(user_ids))
    frequent = rng.choice(len(user_ids), size=15, replace=False)
    weights[frequent] *= 4.0
    weights /= weights.sum()

    dates = pd.to_datetime(rng.choice(pd.date_range(start_date, end_date, freq="D"), size=n))
    product_popularity = np.exp(-np.arange(len(products)) / 16)
    product_popularity /= product_popularity.sum()

    rows = []
    for oid in range(1, n + 1):
        uid = int(rng.choice(user_ids, p=weights))
        status = str(rng.choice(
            ["delivered", "shipped", "processing", "cancelled", "returned"],
            p=[0.68, 0.12, 0.10, 0.06, 0.04]
        ))
        method = str(rng.choice(
            ["credit_card", "debit_card", "paypal", "bank_transfer", "cash_on_delivery"],
            p=[0.34, 0.28, 0.16, 0.10, 0.12]
        ))
        rows.append({
            "order_id": oid,
            "user_id": uid,
            "order_date": dates[oid - 1].strftime("%Y-%m-%d"),
            "order_status": status,
            "payment_method": method,
            "total_amount": 0.0
        })
    return pd.DataFrame(rows), product_popularity
import numpy as np
import pandas as pd

def generate_order_items(orders, products, rng, product_popularity):
    rows = []
    iid = 1
    product_ids = products["product_id"].to_numpy()
    pop = product_popularity / product_popularity.sum()
    price_map = products.set_index("product_id")["price"].to_dict()
    discount_map = products.set_index("product_id")["discount_percent"].to_dict()

    for _, order in orders.iterrows():
        count = int(rng.choice([1, 2, 3, 4, 5], p=[0.30, 0.36, 0.20, 0.10, 0.04]))
        chosen = rng.choice(product_ids, size=count, replace=False, p=pop)
        total = 0.0
        for pid in chosen:
            qty = int(rng.choice([1, 2, 3, 4], p=[0.70, 0.20, 0.08, 0.02]))
            unit = round(price_map[int(pid)] * (1 - discount_map[int(pid)] / 100), 2)
            rows.append({
                "order_item_id": iid,
                "order_id": int(order["order_id"]),
                "product_id": int(pid),
                "quantity": qty,
                "unit_price": unit,
                "line_total": round(qty * unit, 2)
            })
            total += qty * unit
            iid += 1
        orders.loc[orders["order_id"] == order["order_id"], "total_amount"] = round(total, 2)
    return pd.DataFrame(rows), orders
import numpy as np
import pandas as pd

def generate_payments(orders, rng):
    rows = []
    for _, order in orders.iterrows():
        status = order["order_status"]
        if status == "cancelled":
            payment_status = str(rng.choice(["failed", "refunded"], p=[0.65, 0.35]))
        elif status == "returned":
            payment_status = "refunded"
        else:
            payment_status = str(rng.choice(["paid", "paid", "pending"], p=[0.85, 0.10, 0.05]))
        rows.append({
            "payment_id": int(order["order_id"]),
            "order_id": int(order["order_id"]),
            "payment_date": order["order_date"],
            "payment_method": order["payment_method"],
            "payment_status": payment_status,
            "amount": float(order["total_amount"])
        })
    return pd.DataFrame(rows)
import numpy as np
import pandas as pd

NAMES = {
    "Electronics": ["Wireless Headphones", "Bluetooth Speaker", "Smart Watch", "USB-C Hub", "Power Bank", "Mechanical Keyboard", "Wireless Mouse"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender", "Desk Lamp", "Water Bottle", "Non-Stick Pan", "Storage Organizer"],
    "Fashion": ["Running Shoes", "Cotton Hoodie", "Denim Jacket", "Casual Shirt", "Backpack", "Sunglasses", "Sports Cap"],
    "Books": ["Python Programming", "Data Science Handbook", "Clean Code", "Deep Learning", "Algorithms in Practice", "Database Systems", "Cloud Computing"],
    "Sports & Fitness": ["Yoga Mat", "Resistance Bands", "Dumbbells", "Fitness Tracker", "Football", "Skipping Rope", "Gym Gloves"],
    "Beauty": ["Face Wash", "Moisturizer", "Sunscreen", "Shampoo", "Perfume", "Lip Balm", "Hair Dryer"],
    "Office": ["Notebook", "Gel Pens", "Desk Organizer", "Office Chair", "Monitor Stand", "Planner", "Whiteboard"],
    "Gaming": ["Gaming Mouse", "Gaming Keyboard", "Controller", "Webcam", "Gaming Headset", "Mouse Pad", "Gamepad Stand"]
}

def generate_products(n, rng):
    categories = list(NAMES)
    rows = []
    used = set()
    for pid in range(1, n + 1):
        category = categories[(pid - 1) % len(categories)]
        base = NAMES[category][(pid - 1) % len(NAMES[category])]
        suffix = (pid - 1) // len(categories) + 1
        name = base if suffix == 1 else f"{base} {suffix}"
        price_ranges = {
            "Electronics": (1800, 55000), "Home & Kitchen": (700, 22000),
            "Fashion": (800, 18000), "Books": (700, 6500),
            "Sports & Fitness": (600, 18000), "Beauty": (500, 12000),
            "Office": (250, 30000), "Gaming": (1200, 45000)
        }
        lo, hi = price_ranges[category]
        price = round(float(rng.uniform(lo, hi)), 2)
        discount = int(rng.choice([0, 0, 5, 10, 15, 20, 25]))
        stock = int(rng.integers(8, 180))
        rating = round(float(np.clip(rng.normal(4.05, 0.45), 2.5, 5.0)), 2)
        rows.append({
            "product_id": pid,
            "product_name": name,
            "category": category,
            "price": price,
            "discount_percent": discount,
            "stock": stock,
            "rating": rating
        })
    return pd.DataFrame(rows)
import numpy as np
import pandas as pd

def generate_reviews(n, users, products, orders, rng):
    # Reviews only reference products actually bought by the user.
    pairs = orders[["user_id", "order_id"]].merge(
        pd.DataFrame(), how="left", left_index=True, right_index=True
    ) if False else None

    item_source = None
    # This function receives orders only; main passes a temporary order-item frame.
    raise RuntimeError("Use generate_reviews_with_items from main.py")

def generate_reviews_with_items(n, users, products, orders, order_items, rng):
    valid = order_items.merge(
        orders[["order_id", "user_id", "order_date"]],
        on="order_id", how="inner"
    )[["user_id", "product_id", "order_date"]].drop_duplicates()

    sample = valid.sample(n=n, random_state=42, replace=False)
    product_rating = products.set_index("product_id")["rating"].to_dict()
    rows = []
    for rid, (_, r) in enumerate(sample.iterrows(), start=1):
        base = product_rating[int(r["product_id"])]
        rating = int(np.clip(round(rng.normal(base, 0.65)), 1, 5))
        title = rng.choice(["Good value", "Works well", "Worth buying", "Decent product", "Excellent quality"])
        rows.append({
            "review_id": rid,
            "user_id": int(r["user_id"]),
            "product_id": int(r["product_id"]),
            "rating": rating,
            "review_title": title,
            "review_date": r["order_date"]
        })
    return pd.DataFrame(rows)
import numpy as np
import pandas as pd
from faker import Faker

def generate_users(n, fake, rng, start_date, end_date):
    registration_dates = pd.to_datetime(
        rng.choice(pd.date_range(start_date, end_date, freq="D"), size=n)
    )
    registration_dates = sorted(registration_dates)

    rows = []
    for i in range(1, n + 1):
        first = fake.first_name()
        last = fake.last_name()
        rows.append({
            "user_id": i,
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}.{i}@example.com",
            "city": fake.city(),
            "country": "Pakistan",
            "registration_date": registration_dates[i - 1].strftime("%Y-%m-%d"),
        })
    return pd.DataFrame(rows)
import pandas as pd

def generate_data_dictionary(output_path):
    rows = [
        ("users","user_id","integer","Primary key","Unique user identifier"),
        ("users","first_name","string","","User first name"),
        ("users","last_name","string","","User last name"),
        ("users","email","string","Unique","Synthetic email address"),
        ("users","city","string","","User city"),
        ("users","country","string","","User country"),
        ("users","registration_date","date","","Account registration date"),
        ("products","product_id","integer","Primary key","Unique product identifier"),
        ("products","product_name","string","","Product name"),
        ("products","category","string","","Product category"),
        ("products","price","decimal","","List price in PKR"),
        ("products","discount_percent","integer","","Discount percentage"),
        ("products","stock","integer","","Available inventory"),
        ("products","rating","decimal","","Synthetic product rating from 2.5 to 5.0"),
        ("orders","order_id","integer","Primary key","Unique order identifier"),
        ("orders","user_id","integer","Foreign key -> users.user_id","Customer placing the order"),
        ("orders","order_date","date","","Order date"),
        ("orders","order_status","string","","Order lifecycle status"),
        ("orders","payment_method","string","","Selected payment method"),
        ("orders","total_amount","decimal","","Sum of order item line totals"),
        ("order_items","order_item_id","integer","Primary key","Unique line-item identifier"),
        ("order_items","order_id","integer","Foreign key -> orders.order_id","Parent order"),
        ("order_items","product_id","integer","Foreign key -> products.product_id","Purchased product"),
        ("order_items","quantity","integer","","Units purchased"),
        ("order_items","unit_price","decimal","","Discounted unit price"),
        ("order_items","line_total","decimal","","quantity * unit_price"),
        ("payments","payment_id","integer","Primary key","One payment record per order"),
        ("payments","order_id","integer","Foreign key -> orders.order_id","Paid order"),
        ("payments","payment_date","date","","Payment date"),
        ("payments","payment_method","string","","Payment method"),
        ("payments","payment_status","string","","Payment result/status"),
        ("payments","amount","decimal","","Payment amount"),
        ("reviews","review_id","integer","Primary key","Unique review identifier"),
        ("reviews","user_id","integer","Foreign key -> users.user_id","Reviewer"),
        ("reviews","product_id","integer","Foreign key -> products.product_id","Reviewed product"),
        ("reviews","rating","integer","","Rating from 1 to 5"),
        ("reviews","review_title","string","","Short synthetic review title"),
        ("reviews","review_date","date","","Review date"),
        ("user_events","event_id","integer","Primary key","Unique event identifier"),
        ("user_events","user_id","integer","Foreign key -> users.user_id","User generating event"),
        ("user_events","event_type","string","","Behavioral event type"),
        ("user_events","product_id","integer","Foreign key -> products.product_id; nullable","Related product where applicable"),
        ("user_events","search_query","string","Nullable","Search phrase for search events"),
        ("user_events","event_timestamp","datetime","","Event timestamp"),
    ]
    pd.DataFrame(rows, columns=["table_name","column_name","data_type","key_or_constraint","description"]).to_csv(
        output_path, index=False
    )
import json
from pathlib import Path
import pandas as pd

def validate_and_statistics(tables, output_dir):
    users = tables["users"]; products = tables["products"]; orders = tables["orders"]
    items = tables["order_items"]; payments = tables["payments"]
    reviews = tables["reviews"]; events = tables["user_events"]

    errors = []

    checks = [
        ("users.user_id", users["user_id"].is_unique),
        ("products.product_id", products["product_id"].is_unique),
        ("orders.order_id", orders["order_id"].is_unique),
        ("order_items.order_item_id", items["order_item_id"].is_unique),
        ("payments.payment_id", payments["payment_id"].is_unique),
        ("reviews.review_id", reviews["review_id"].is_unique),
        ("events.event_id", events["event_id"].is_unique),
    ]
    errors += [f"Duplicate IDs: {name}" for name, ok in checks if not ok]

    def fk(child, col, parent, pcol):
        return set(child[col].dropna()).issubset(set(parent[pcol]))

    for child, col, parent, pcol in [
        (orders, "user_id", users, "user_id"),
        (items, "order_id", orders, "order_id"),
        (items, "product_id", products, "product_id"),
        (payments, "order_id", orders, "order_id"),
        (reviews, "user_id", users, "user_id"),
        (reviews, "product_id", products, "product_id"),
        (events, "user_id", users, "user_id"),
        (events, "product_id", products, "product_id"),
    ]:
        if not fk(child, col, parent, pcol):
            errors.append(f"Broken foreign key: {col}")

    if (products["price"] < 0).any() or (products["stock"] < 0).any():
        errors.append("Invalid product price/stock")
    if (items["quantity"] <= 0).any() or (items["unit_price"] < 0).any() or (items["line_total"] < 0).any():
        errors.append("Invalid order item values")
    if (orders["total_amount"] < 0).any() or (payments["amount"] < 0).any():
        errors.append("Negative monetary amount")
    if not items.groupby("order_id")["line_total"].sum().round(2).equals(
        orders.set_index("order_id")["total_amount"].sort_index().round(2)
    ):
        errors.append("Inconsistent order totals")

    date_cols = [
        ("users", "registration_date"), ("orders", "order_date"),
        ("payments", "payment_date"), ("reviews", "review_date"),
        ("user_events", "event_timestamp")
    ]
    for name, col in date_cols:
        parsed = pd.to_datetime(tables[name][col], errors="coerce")
        if parsed.isna().any():
            errors.append(f"Invalid dates in {name}.{col}")

    if not reviews["rating"].between(1, 5).all():
        errors.append("Review rating outside 1-5")
    if len(items) < 1000:
        errors.append("Fewer than 1,000 order items")

    stats = {
        "random_seed": 42,
        "row_counts": {name: int(len(df)) for name, df in tables.items()},
        "column_counts": {name: int(len(df.columns)) for name, df in tables.items()},
        "validation": {"passed": len(errors) == 0, "errors": errors},
        "summary": {
            "total_order_value": round(float(orders["total_amount"].sum()), 2),
            "average_order_value": round(float(orders["total_amount"].mean()), 2),
            "average_review_rating": round(float(reviews["rating"].mean()), 2),
            "top_product_by_orders": int(items.groupby("product_id")["order_id"].nunique().idxmax()),
            "top_event_type": str(events["event_type"].value_counts().idxmax()),
        }
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "dataset_statistics.json").write_text(
        json.dumps(stats, indent=2), encoding="utf-8"
    )
    if errors:
        raise ValueError("Dataset validation failed: " + "; ".join(errors))
    return stats
