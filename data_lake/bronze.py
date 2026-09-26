import os
import pandas as pd


class BronzeLayer:

    def __init__(
        self,
        input_path="data/raw",
        output_path="data/lake/bronze"
    ):
        self.input_path = input_path
        self.output_path = output_path

        os.makedirs(self.output_path, exist_ok=True)

    def load(self):

        files = {
            "users": "users.csv",
            "products": "products.csv",
            "orders": "orders.csv",
            "order_items": "order_items.csv",
            "payments": "payments.csv",
            "reviews": "reviews.csv",
            "events": "user_events.csv"
        }

        print("\nCreating Bronze Layer...")

        for name, filename in files.items():

            input_file = os.path.join(
                self.input_path,
                filename
            )

            output_file = os.path.join(
                self.output_path,
                f"{name}.parquet"
            )

            print(f"Processing {filename}...")

            df = pd.read_csv(input_file)

            df.to_parquet(
                output_file,
                engine="pyarrow",
                index=False
            )

            print(f"Saved: {output_file}")

        print("\nBronze layer completed.")