from .validate import DataValidator


def main():

    validator = DataValidator()

    report = validator.run()

    if report["status"] == "PASSED":

        print(
            "\nAll validation checks passed!"
        )

    else:

        print(
            "\nValidation failed."
        )


if __name__ == "__main__":

    main()