from .extract import DataExtractor
from .transform import DataTransformer
from .load import DataLoader


def main():

    print("=" * 60)
    print("BATCH ETL PIPELINE")
    print("=" * 60)

    # Extract
    extractor = DataExtractor()

    raw_data = extractor.extract()

    # Transform
    transformer = DataTransformer()

    transformed_data = transformer.transform(
        raw_data
    )

    # Load
    loader = DataLoader()

    loader.load(
        transformed_data
    )

    print("\n" + "=" * 60)
    print("ETL PIPELINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()