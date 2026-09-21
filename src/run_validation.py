from src.extract import extract
from src.transform import transform
from src.validation import validate_all


def main():
    print("=" * 70)
    print("HOSPITAL DATA QUALITY VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Extract
    # --------------------------------------------------------

    print("\n[1] Extracting raw data...")

    raw_data = extract()

    for name, df in raw_data.items():
        print(f"{name:20s}: {len(df):6d} rows")

    # --------------------------------------------------------
    # Transform
    # --------------------------------------------------------

    print("\n[2] Transforming data...")

    transformed_data = transform(raw_data)

    for name, df in transformed_data.items():
        print(f"{name:20s}: {len(df):6d} rows")

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    print("\n[3] Running data-quality checks...")

    result = validate_all(
        transformed_data,
        raise_on_error=False,
    )

    print("\n" + "-" * 70)
    print("VALIDATION RESULT")
    print("-" * 70)

    print(f"Status      : {result['status']}")
    print(f"Error count : {result['error_count']}")

    if result["errors"]:
        print("\nVALIDATION ERRORS")
        print("-" * 70)

        for error in result["errors"]:
            print(f"❌ {error}")
    else:
        print("\n✅ All data-quality checks passed.")

    print("=" * 70)


if __name__ == "__main__":
    main()