from .bronze import BronzeLayer
from .silver import SilverLayer
from .gold import GoldLayer


def main():

    print("=" * 60)
    print("LOCAL DATA LAKE PIPELINE")
    print("=" * 60)

    # Bronze Layer
    bronze = BronzeLayer()
    bronze.load()

    # Silver Layer
    silver = SilverLayer()
    silver.load()

    # Gold Layer
    gold = GoldLayer()
    gold.load()

    print("\n" + "=" * 60)
    print("DATA LAKE PIPELINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()