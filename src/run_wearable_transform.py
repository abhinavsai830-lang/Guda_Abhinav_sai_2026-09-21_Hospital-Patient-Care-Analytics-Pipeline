"""
Development runner for wearable-data transformation.

Run from project root:

    python -m src.run_wearable_transform
"""

from src.extract import extract_wearables
from src.transform import transform_wearables


def main() -> None:

    # --------------------------------------------------------
    # Extract
    # --------------------------------------------------------

    raw = extract_wearables()

    # --------------------------------------------------------
    # Transform
    # --------------------------------------------------------

    clean = transform_wearables(
        raw
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("=" * 70)
    print("WEARABLE TRANSFORMATION")
    print("=" * 70)

    print(
        f"Raw rows            : {len(raw)}"
    )

    print(
        f"Clean rows          : {len(clean)}"
    )

    print(
        f"Rows removed        : "
        f"{len(raw) - len(clean)}"
    )

    print(
        f"Unique devices      : "
        f"{clean['device_id'].nunique()}"
    )

    print(
        f"Abnormal HR rows    : "
        f"{clean['heart_rate_abnormal'].sum()}"
    )

    print(
        f"Abnormal SpO2 rows  : "
        f"{clean['spo2_abnormal'].sum()}"
    )

    print(
        f"Abnormal temp rows  : "
        f"{clean['body_temp_abnormal'].sum()}"
    )

    print(
        f"Any abnormal vital  : "
        f"{clean['is_abnormal'].sum()}"
    )

    print()
    print("Transformed sample:")

    print(
        clean.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()