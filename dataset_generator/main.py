import numpy as np
from faker import Faker

from dataset_generator.config import (
    OUTPUT_DIR, RANDOM_SEED, N_USERS, N_PRODUCTS,
    N_ORDERS, N_REVIEWS, N_EVENTS, START_DATE, END_DATE
)
from dataset_generator.generator import (
    generate_users,
    generate_products,
    generate_orders,
    generate_order_items,
    generate_payments,
    generate_reviews_with_items,
    generate_events,
    generate_data_dictionary,
    validate_and_statistics
)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    np.random.seed(RANDOM_SEED)
    rng = np.random.default_rng(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    users = generate_users(N_USERS, fake, rng, START_DATE, END_DATE)
    products = generate_products(N_PRODUCTS, rng)
    orders, popularity = generate_orders(N_ORDERS, users, products, rng, START_DATE, END_DATE)
    order_items, orders = generate_order_items(orders, products, rng, popularity)
    payments = generate_payments(orders, rng)
    reviews = generate_reviews_with_items(N_REVIEWS, users, products, orders, order_items, rng)
    events = generate_events(N_EVENTS, users, products, orders, rng)

    tables = {
        "users": users,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "reviews": reviews,
        "user_events": events,
    }

    for name, df in tables.items():
        df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)

    generate_data_dictionary(OUTPUT_DIR / "data_dictionary.csv")
    stats = validate_and_statistics(tables, OUTPUT_DIR)

    print("Dataset generated successfully.")
    print(f"Output directory: {OUTPUT_DIR}")
    print("Validation passed:", stats["validation"]["passed"])
    for name, count in stats["row_counts"].items():
        print(f"  {name}: {count:,} rows")

if __name__ == "__main__":
    main()
