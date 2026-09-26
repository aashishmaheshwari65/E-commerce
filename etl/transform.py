import pandas as pd


class DataTransformer:

    def transform_users(self, users):

        users = users.copy()

        users["email"] = (
            users["email"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        users["first_name"] = (
            users["first_name"]
            .astype(str)
            .str.strip()
        )

        users["last_name"] = (
            users["last_name"]
            .astype(str)
            .str.strip()
        )

        users["city"] = (
            users["city"]
            .astype(str)
            .str.strip()
        )

        users["country"] = (
            users["country"]
            .astype(str)
            .str.strip()
        )

        users["registration_date"] = pd.to_datetime(
            users["registration_date"],
            errors="coerce"
        )

        return users


    def transform_products(self, products):

        products = products.copy()

        products["product_name"] = (
            products["product_name"]
            .astype(str)
            .str.strip()
        )

        products["category"] = (
            products["category"]
            .astype(str)
            .str.strip()
        )

        products["price"] = pd.to_numeric(
            products["price"],
            errors="coerce"
        )

        products["discount_percent"] = pd.to_numeric(
            products["discount_percent"],
            errors="coerce"
        )

        products["stock"] = pd.to_numeric(
            products["stock"],
            errors="coerce"
        )

        products["rating"] = pd.to_numeric(
            products["rating"],
            errors="coerce"
        )

        # Calculate discounted price
        products["discount_amount"] = (
            products["price"] *
            products["discount_percent"] / 100
        ).round(2)

        products["final_price"] = (
            products["price"] -
            products["discount_amount"]
        ).round(2)

        return products


    def transform_orders(self, orders):

        orders = orders.copy()

        orders["order_date"] = pd.to_datetime(
            orders["order_date"],
            errors="coerce"
        )

        orders["total_amount"] = pd.to_numeric(
            orders["total_amount"],
            errors="coerce"
        )

        orders["order_status"] = (
            orders["order_status"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        orders["payment_method"] = (
            orders["payment_method"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        return orders


    def transform_order_items(self, order_items):

        order_items = order_items.copy()

        order_items["quantity"] = pd.to_numeric(
            order_items["quantity"],
            errors="coerce"
        )

        order_items["unit_price"] = pd.to_numeric(
            order_items["unit_price"],
            errors="coerce"
        )

        # Recalculate line total
        order_items["line_total"] = (
            order_items["quantity"] *
            order_items["unit_price"]
        ).round(2)

        return order_items


    def transform_payments(self, payments):

        payments = payments.copy()

        payments["payment_date"] = pd.to_datetime(
            payments["payment_date"],
            errors="coerce"
        )

        payments["amount"] = pd.to_numeric(
            payments["amount"],
            errors="coerce"
        )

        payments["payment_method"] = (
            payments["payment_method"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        payments["payment_status"] = (
            payments["payment_status"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        return payments


    def transform_reviews(self, reviews):

        reviews = reviews.copy()

        reviews["rating"] = pd.to_numeric(
            reviews["rating"],
            errors="coerce"
        )

        reviews["review_date"] = pd.to_datetime(
            reviews["review_date"],
            errors="coerce"
        )

        reviews["review_title"] = (
            reviews["review_title"]
            .astype(str)
            .str.strip()
        )

        return reviews


    def transform_events(self, events):

        events = events.copy()

        events["event_timestamp"] = pd.to_datetime(
            events["event_timestamp"],
            errors="coerce"
        )

        events["event_type"] = (
            events["event_type"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        events["search_query"] = (
            events["search_query"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        return events


    def transform(self, data):

        print("\nTransforming data...")

        transformed = {}

        transformed["users"] = self.transform_users(
            data["users"]
        )

        transformed["products"] = self.transform_products(
            data["products"]
        )

        transformed["orders"] = self.transform_orders(
            data["orders"]
        )

        transformed["order_items"] = (
            self.transform_order_items(
                data["order_items"]
            )
        )

        transformed["payments"] = (
            self.transform_payments(
                data["payments"]
            )
        )

        transformed["reviews"] = (
            self.transform_reviews(
                data["reviews"]
            )
        )

        transformed["events"] = (
            self.transform_events(
                data["events"]
            )
        )

        return transformed