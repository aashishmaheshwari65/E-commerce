import os
import pandas as pd


class GoldLayer:

    def __init__(
        self,
        input_path="data/lake/silver",
        output_path="data/lake/gold"
    ):
        self.input_path = input_path
        self.output_path = output_path

        os.makedirs(self.output_path, exist_ok=True)

    def create_customer_sales(self):

        print("\nCreating customer sales dataset...")

        users = pd.read_parquet(
            os.path.join(
                self.input_path,
                "users.parquet"
            )
        )

        orders = pd.read_parquet(
            os.path.join(
                self.input_path,
                "orders.parquet"
            )
        )

        order_items = pd.read_parquet(
            os.path.join(
                self.input_path,
                "order_items.parquet"
            )
        )

        orders_items = orders.merge(
            order_items,
            on="order_id",
            how="inner"
        )

        customer_sales = orders_items.merge(
            users,
            on="user_id",
            how="left"
        )

        customer_sales = customer_sales[
            [
                "order_id",
                "user_id",
                "first_name",
                "last_name",
                "city",
                "country",
                "registration_date",
                "order_date",
                "order_status",
                "payment_method",
                "product_id",
                "quantity",
                "unit_price",
                "line_total"
            ]
        ]

        output_file = os.path.join(
            self.output_path,
            "customer_sales.parquet"
        )

        customer_sales.to_parquet(
            output_file,
            engine="pyarrow",
            index=False
        )

        print(f"Saved: {output_file}")

    def create_product_sales(self):

        print("\nCreating product sales dataset...")

        products = pd.read_parquet(
            os.path.join(
                self.input_path,
                "products.parquet"
            )
        )

        order_items = pd.read_parquet(
            os.path.join(
                self.input_path,
                "order_items.parquet"
            )
        )

        product_sales = order_items.merge(
            products,
            on="product_id",
            how="left"
        )

        product_sales = product_sales[
            [
                "product_id",
                "product_name",
                "category",
                "price",
                "discount_percent",
                "final_price",
                "quantity",
                "line_total",
                "rating"
            ]
        ]

        output_file = os.path.join(
            self.output_path,
            "product_sales.parquet"
        )

        product_sales.to_parquet(
            output_file,
            engine="pyarrow",
            index=False
        )

        print(f"Saved: {output_file}")

    def load(self):

        self.create_customer_sales()
        self.create_product_sales()

        print("\nGold layer completed.")