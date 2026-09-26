import os
import pandas as pd


class SilverLayer:

    def __init__(
        self,
        input_path="data/processed",
        output_path="data/lake/silver"
    ):
        self.input_path = input_path
        self.output_path = output_path

        os.makedirs(self.output_path, exist_ok=True)

    def load(self):

        files = {
            "users": "users_clean.csv",
            "products": "products_clean.csv",
            "orders": "orders_clean.csv",
            "order_items": "order_items_clean.csv",
            "payments": "payments_clean.csv",
            "reviews": "reviews_clean.csv",
            "events": "user_events_clean.csv"
        }

        print("\nCreating Silver Layer...")

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

        print("\nSilver layer completed.")