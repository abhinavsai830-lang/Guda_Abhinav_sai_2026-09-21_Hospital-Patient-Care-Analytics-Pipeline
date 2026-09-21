"""
Development runner for laboratory transformation.

Run from project root:

    python -m src.run_lab_transform
"""

from src.extract import (
    extract_lab_reports,
    extract_patients,
)

from src.transform import (
    transform_lab_reports,
)


def main() -> None:

    # --------------------------------------------------------
    # Extract
    # --------------------------------------------------------

    patients = extract_patients()

    labs = extract_lab_reports()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    # --------------------------------------------------------
    # Transform
    # --------------------------------------------------------

    clean = transform_lab_reports(
        labs,
        valid_patient_ids,
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("=" * 70)
    print("LABORATORY TRANSFORMATION")
    print("=" * 70)

    print(
        f"Raw rows         : {len(labs)}"
    )

    print(
        f"Clean rows       : {len(clean)}"
    )

    print(
        f"Rows removed     : "
        f"{len(labs) - len(clean)}"
    )

    print(
        f"Normal results   : "
        f"{(clean['result_status'] == 'Normal').sum()}"
    )

    print(
        f"Low results      : "
        f"{(clean['result_status'] == 'Low').sum()}"
    )

    print(
        f"High results     : "
        f"{(clean['result_status'] == 'High').sum()}"
    )

    print(
        f"Abnormal results : "
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