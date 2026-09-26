import os
import pandas as pd


class DataExtractor:

    def __init__(self, data_path="data/raw"):
        self.data_path = data_path

    def extract(self):

        files = {
            "users": "users.csv",
            "products": "products.csv",
            "orders": "orders.csv",
            "order_items": "order_items.csv",
            "payments": "payments.csv",
            "reviews": "reviews.csv",
            "events": "user_events.csv"
        }

        data = {}

        for name, filename in files.items():

            path = os.path.join(
                self.data_path,
                filename
            )

            print(f"Extracting {filename}...")

            data[name] = pd.read_csv(path)

        return data