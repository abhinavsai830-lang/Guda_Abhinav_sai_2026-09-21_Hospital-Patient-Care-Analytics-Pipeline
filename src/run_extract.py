"""
Small development runner for the extraction stage.

Run from project root:

    python -m src.run_extract
"""

from src.extract import extract


def main() -> None:

    raw_data = extract()

    print("=" * 70)
    print("EXTRACTION RESULTS")
    print("=" * 70)

    for name, df in raw_data.items():

        print()
        print(f"SOURCE: {name}")

        print("-" * 70)

        print(
            f"Rows    : {len(df)}"
        )

        print(
            f"Columns : {len(df.columns)}"
        )

        print(
            f"Columns : {list(df.columns)}"
        )

        print()
        print(
            df.head(3).to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()