"""
Development runner for patient transformation.

Run from the project root:

    python -m src.run_transform
"""

from src.extract import extract_patients
from src.transform import transform_patients


def main() -> None:
    """
    Extract raw patient data, transform it,
    and display the results.
    """

    # --------------------------------------------------------
    # STEP 1: Extract
    # --------------------------------------------------------

    raw = extract_patients()

    # --------------------------------------------------------
    # STEP 2: Transform
    # --------------------------------------------------------

    clean = transform_patients(raw)

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print("=" * 70)
    print("PATIENT TRANSFORMATION")
    print("=" * 70)

    print(
        f"Raw rows           : {len(raw)}"
    )

    print(
        f"Clean rows         : {len(clean)}"
    )

    print(
        f"Duplicates removed : "
        f"{len(raw) - len(clean)}"
    )

    print()

    print("Transformed columns:")
    print(
        clean.columns.tolist()
    )

    print()

    print("Sample transformed records:")

    print(
        clean.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()