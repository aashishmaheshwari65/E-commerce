from pathlib import Path

RANDOM_SEED = 42

N_USERS = 100
N_PRODUCTS = 50
N_ORDERS = 500
N_REVIEWS = 200
N_EVENTS = 5000

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

START_DATE = "2024-01-01"
END_DATE = "2026-08-31"

CATEGORIES = [
    "Electronics", "Home & Kitchen", "Fashion", "Books",
    "Sports & Fitness", "Beauty", "Office", "Gaming"
]

PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer", "cash_on_delivery"]
ORDER_STATUSES = ["delivered", "shipped", "processing", "cancelled", "returned"]
EVENT_TYPES = [
    "page_view", "product_view", "search", "add_to_cart",
    "wishlist", "checkout", "purchase"
]
