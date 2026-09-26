import os


class DataLoader:

    def __init__(self, output_path="data/processed"):

        self.output_path = output_path

        os.makedirs(
            self.output_path,
            exist_ok=True
        )

    def load(self, data):

        print("\nLoading transformed data...")

        file_names = {
            "users": "users_clean.csv",
            "products": "products_clean.csv",
            "orders": "orders_clean.csv",
            "order_items": "order_items_clean.csv",
            "payments": "payments_clean.csv",
            "reviews": "reviews_clean.csv",
            "events": "user_events_clean.csv"
        }

        for name, filename in file_names.items():

            path = os.path.join(
                self.output_path,
                filename
            )

            data[name].to_csv(
                path,
                index=False
            )

            print(f"Saved: {path}")