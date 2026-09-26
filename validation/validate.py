import os
import json
import pandas as pd

from .rules import ValidationRules


class DataValidator:

    def __init__(self):

        self.data_path = "data/raw"
        self.report_path = "data/validation"

        os.makedirs(
            self.report_path,
            exist_ok=True
        )

    # ============================================================
    # LOAD DATA
    # ============================================================

    def load_data(self):

        data = {}

        files = {
            "users": "users.csv",
            "products": "products.csv",
            "orders": "orders.csv",
            "order_items": "order_items.csv",
            "payments": "payments.csv",
            "reviews": "reviews.csv",
            "events": "user_events.csv"
        }

        for name, filename in files.items():

            path = os.path.join(
                self.data_path,
                filename
            )

            print(f"Loading {filename}...")

            data[name] = pd.read_csv(path)

        return data

    # ============================================================
    # RUN VALIDATION
    # ============================================================

    def run(self):

        print("\n" + "=" * 60)
        print("DATA VALIDATION STARTED")
        print("=" * 60)

        data = self.load_data()

        errors = []

        # --------------------------------------------------------
        # USERS
        # --------------------------------------------------------

        print("\nValidating users...")

        errors.extend(
            ValidationRules.validate_users(
                data["users"]
            )
        )

        # --------------------------------------------------------
        # PRODUCTS
        # --------------------------------------------------------

        print("Validating products...")

        errors.extend(
            ValidationRules.validate_products(
                data["products"]
            )
        )

        # --------------------------------------------------------
        # ORDERS
        # --------------------------------------------------------

        print("Validating orders...")

        errors.extend(
            ValidationRules.validate_orders(
                data["orders"],
                data["users"]
            )
        )

        # --------------------------------------------------------
        # ORDER ITEMS
        # --------------------------------------------------------

        print("Validating order items...")

        errors.extend(
            ValidationRules.validate_order_items(
                data["order_items"],
                data["orders"],
                data["products"]
            )
        )

        # --------------------------------------------------------
        # PAYMENTS
        # --------------------------------------------------------

        print("Validating payments...")

        errors.extend(
            ValidationRules.validate_payments(
                data["payments"],
                data["orders"]
            )
        )

        # --------------------------------------------------------
        # REVIEWS
        # --------------------------------------------------------

        print("Validating reviews...")

        errors.extend(
            ValidationRules.validate_reviews(
                data["reviews"],
                data["users"],
                data["products"]
            )
        )

        # --------------------------------------------------------
        # EVENTS
        # --------------------------------------------------------

        print("Validating user events...")

        errors.extend(
            ValidationRules.validate_events(
                data["events"],
                data["users"],
                data["products"]
            )
        )

        # ========================================================
        # REPORT
        # ========================================================

        status = "PASSED" if not errors else "FAILED"

        report = {
            "status": status,
            "total_errors": len(errors),
            "errors": errors
        }

        report_file = os.path.join(
            self.report_path,
            "validation_report.json"
        )

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        # ========================================================
        # RESULT
        # ========================================================

        print("\n" + "=" * 60)
        print("VALIDATION RESULT")
        print("=" * 60)

        print(f"Status: {status}")
        print(f"Total errors: {len(errors)}")

        if errors:

            print("\nValidation Errors:")

            for i, error in enumerate(
                errors,
                start=1
            ):
                print(f"{i}. {error}")

        else:

            print(
                "\nAll validation checks passed!"
            )

        print(
            f"\nReport saved to: {report_file}"
        )

        print("=" * 60)

        return report