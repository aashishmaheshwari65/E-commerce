import re


class ValidationRules:

    # ============================================================
    # USERS
    # ============================================================

    @staticmethod
    def validate_users(users):

        errors = []

        # Required columns
        required_columns = [
            "user_id",
            "first_name",
            "last_name",
            "email",
            "city",
            "country",
            "registration_date"
        ]

        missing = [
            col for col in required_columns
            if col not in users.columns
        ]

        if missing:
            errors.append(
                f"Missing columns in users.csv: {missing}"
            )
            return errors

        # user_id uniqueness
        if users["user_id"].duplicated().any():
            errors.append("Duplicate user_id found.")

        # email uniqueness
        if users["email"].duplicated().any():
            errors.append("Duplicate email found.")

        # missing emails
        if users["email"].isnull().any():
            errors.append("Missing email found.")

        # email format
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        invalid_emails = users[
            ~users["email"].astype(str).str.match(
                email_pattern,
                na=False
            )
        ]

        if not invalid_emails.empty:
            errors.append(
                f"Invalid email format found: "
                f"{len(invalid_emails)} records."
            )

        # names
        if users["first_name"].isnull().any():
            errors.append("Missing first_name found.")

        if users["last_name"].isnull().any():
            errors.append("Missing last_name found.")

        # registration date
        registration_dates = users["registration_date"]

        invalid_dates = registration_dates[
            registration_dates.notna()
        ].apply(
            lambda x: __import__("pandas").to_datetime(
                x,
                errors="coerce"
            )
        )

        if invalid_dates.isna().any():
            errors.append(
                "Invalid registration_date found."
            )

        return errors

    # ============================================================
    # PRODUCTS
    # ============================================================

    @staticmethod
    def validate_products(products):

        errors = []

        required_columns = [
            "product_id",
            "product_name",
            "category",
            "price",
            "discount_percent",
            "stock",
            "rating"
        ]

        missing = [
            col for col in required_columns
            if col not in products.columns
        ]

        if missing:
            errors.append(
                f"Missing columns in products.csv: {missing}"
            )
            return errors

        # Product ID uniqueness
        if products["product_id"].duplicated().any():
            errors.append("Duplicate product_id found.")

        # Product name
        if products["product_name"].isnull().any():
            errors.append("Missing product_name found.")

        # Price
        if (products["price"] < 0).any():
            errors.append(
                "Negative product price found."
            )

        # Discount
        if (
            (products["discount_percent"] < 0) |
            (products["discount_percent"] > 100)
        ).any():
            errors.append(
                "Invalid discount_percent found. "
                "Must be between 0 and 100."
            )

        # Stock
        if (products["stock"] < 0).any():
            errors.append(
                "Negative stock value found."
            )

        # Rating
        if (
            (products["rating"] < 0) |
            (products["rating"] > 5)
        ).any():
            errors.append(
                "Invalid product rating found. "
                "Must be between 0 and 5."
            )

        return errors

    # ============================================================
    # ORDERS
    # ============================================================

    @staticmethod
    def validate_orders(orders, users):

        errors = []

        required_columns = [
            "order_id",
            "user_id",
            "order_date",
            "order_status",
            "payment_method",
            "total_amount"
        ]

        missing = [
            col for col in required_columns
            if col not in orders.columns
        ]

        if missing:
            errors.append(
                f"Missing columns in orders.csv: {missing}"
            )
            return errors

        # Order ID uniqueness
        if orders["order_id"].duplicated().any():
            errors.append("Duplicate order_id found.")

        # Foreign key: user_id
        invalid_users = orders[
            ~orders["user_id"].isin(users["user_id"])
        ]

        if not invalid_users.empty:
            errors.append(
                f"Invalid user_id found in orders: "
                f"{len(invalid_users)} records."
            )

        # Total amount
        if (orders["total_amount"] < 0).any():
            errors.append(
                "Negative total_amount found."
            )

        # Order date
        import pandas as pd

        invalid_dates = pd.to_datetime(
            orders["order_date"],
            errors="coerce"
        )

        if invalid_dates.isna().any():
            errors.append(
                "Invalid order_date found."
            )

        return errors

    # ============================================================
    # ORDER ITEMS
    # ============================================================

    @staticmethod
    def validate_order_items(
        order_items,
        orders,
        products
    ):

        errors = []

        required_columns = [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "line_total"
        ]

        missing = [
            col for col in required_columns
            if col not in order_items.columns
        ]

        if missing:
            errors.append(
                f"Missing columns in order_items.csv: {missing}"
            )
            return errors

        # ID uniqueness
        if order_items["order_item_id"].duplicated().any():
            errors.append(
                "Duplicate order_item_id found."
            )

        # Order foreign key
        invalid_orders = order_items[
            ~order_items["order_id"].isin(
                orders["order_id"]
            )
        ]

        if not invalid_orders.empty:
            errors.append(
                f"Invalid order_id found in order_items: "
                f"{len(invalid_orders)} records."
            )

        # Product foreign key
        invalid_products = order_items[
            ~order_items["product_id"].isin(
                products["product_id"]
            )
        ]

        if not invalid_products.empty:
            errors.append(
                f"Invalid product_id found in order_items: "
                f"{len(invalid_products)} records."
            )

        # Quantity
        if (order_items["quantity"] <= 0).any():
            errors.append(
                "Invalid quantity found. "
                "Quantity must be greater than 0."
            )

        # Unit price
        if (order_items["unit_price"] < 0).any():
            errors.append(
                "Negative unit_price found."
            )

        # Line total
        if (order_items["line_total"] < 0).any():
            errors.append(
                "Negative line_total found."
            )

        # Mathematical consistency
        calculated_total = (
            order_items["quantity"] *
            order_items["unit_price"]
        )

        mismatch = (
            calculated_total.round(2) !=
            order_items["line_total"].round(2)
        )

        if mismatch.any():
            errors.append(
                f"line_total calculation mismatch found: "
                f"{mismatch.sum()} records."
            )

        return errors

    # ============================================================
    # PAYMENTS
    # ============================================================

    @staticmethod
    def validate_payments(payments, orders):

        errors = []

        required_columns = [
            "payment_id",
            "order_id",
            "payment_date",
            "payment_method",
            "payment_status",
            "amount"
        ]

        missing = [
            col for col in required_columns
            if col not in payments.columns
        ]

        if missing:
            errors.append(
                f"Missing columns in payments.csv: {missing}"
            )
            return errors

        # Payment ID uniqueness
        if payments["payment_id"].duplicated().any():
            errors.append(
                "Duplicate payment_id found."
            )

        # Order foreign key
        invalid_orders = payments[
            ~payments["order_id"].isin(
                orders["order_id"]
            )
        ]

        if not invalid_orders.empty:
            errors.append(
                f"Invalid order_id found in payments: "
                f"{len(invalid_orders)} records."
            )

        # Amount
        if (payments["amount"] < 0).any():
            errors.append(
                "Negative payment amount found."
            )

        # Payment date
        import pandas as pd

        invalid_dates = pd.to_datetime(
            payments["payment_date"],
            errors="coerce"
        )

        if invalid_dates.isna().any():
            errors.append(
                "Invalid payment_date found."
            )

        return errors

    # ============================================================
    # REVIEWS
    # ============================================================

    @staticmethod
    def validate_reviews(
        reviews,
        users,
        products
    ):

        errors = []

        required_columns = [
            "review_id",
            "user_id",
            "product_id",
            "rating",
            "review_title",
            "review_date"
        ]

        missing = [
            col for col in required_columns
            if col not in reviews.columns
        ]

        if missing:
            errors.append(
                f"Missing columns in reviews.csv: {missing}"
            )
            return errors

        # Review ID uniqueness
        if reviews["review_id"].duplicated().any():
            errors.append(
                "Duplicate review_id found."
            )

        # User foreign key
        invalid_users = reviews[
            ~reviews["user_id"].isin(
                users["user_id"]
            )
        ]

        if not invalid_users.empty:
            errors.append(
                f"Invalid user_id found in reviews: "
                f"{len(invalid_users)} records."
            )

        # Product foreign key
        invalid_products = reviews[
            ~reviews["product_id"].isin(
                products["product_id"]
            )
        ]

        if not invalid_products.empty:
            errors.append(
                f"Invalid product_id found in reviews: "
                f"{len(invalid_products)} records."
            )

        # Rating
        if (
            (reviews["rating"] < 1) |
            (reviews["rating"] > 5)
        ).any():
            errors.append(
                "Invalid review rating found. "
                "Rating must be between 1 and 5."
            )

        # Review date
        import pandas as pd

        invalid_dates = pd.to_datetime(
            reviews["review_date"],
            errors="coerce"
        )

        if invalid_dates.isna().any():
            errors.append(
                "Invalid review_date found."
            )

        return errors

    # ============================================================
    # USER EVENTS
    # ============================================================

    @staticmethod
    def validate_events(
        events,
        users,
        products
    ):

        errors = []

        required_columns = [
            "event_id",
            "user_id",
            "event_type",
            "product_id",
            "search_query",
            "event_timestamp"
        ]

        missing = [
            col for col in required_columns
            if col not in events.columns
        ]

        if missing:
            errors.append(
                f"Missing columns in user_events.csv: {missing}"
            )
            return errors

        # Event ID uniqueness
        if events["event_id"].duplicated().any():
            errors.append(
                "Duplicate event_id found."
            )

        # User foreign key
        invalid_users = events[
            ~events["user_id"].isin(
                users["user_id"]
            )
        ]

        if not invalid_users.empty:
            errors.append(
                f"Invalid user_id found in user_events: "
                f"{len(invalid_users)} records."
            )

        # Product foreign key
        #
        # product_id can be empty for events such as
        # search, login, etc.
        events_with_product = events[
            events["product_id"].notna()
        ]

        invalid_products = events_with_product[
            ~events_with_product["product_id"].isin(
                products["product_id"]
            )
        ]

        if not invalid_products.empty:
            errors.append(
                f"Invalid product_id found in user_events: "
                f"{len(invalid_products)} records."
            )

        # Event type
        if events["event_type"].isnull().any():
            errors.append(
                "Missing event_type found."
            )

        # Event timestamp
        import pandas as pd

        invalid_timestamps = pd.to_datetime(
            events["event_timestamp"],
            errors="coerce"
        )

        if invalid_timestamps.isna().any():
            errors.append(
                "Invalid event_timestamp found."
            )

        return errors