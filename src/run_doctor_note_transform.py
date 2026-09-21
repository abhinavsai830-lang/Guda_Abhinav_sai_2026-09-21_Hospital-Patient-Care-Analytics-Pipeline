"""
Development runner for doctor-note transformation.

Run from project root:

    python -m src.run_doctor_note_transform
"""

from src.extract import extract_doctor_notes
from src.transform import transform_doctor_notes


def main() -> None:

    # --------------------------------------------------------
    # Extract
    # --------------------------------------------------------

    raw = extract_doctor_notes()

    # --------------------------------------------------------
    # Transform
    # --------------------------------------------------------

    clean = transform_doctor_notes(
        raw
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("=" * 70)
    print("DOCTOR NOTE TRANSFORMATION")
    print("=" * 70)

    print(
        f"Raw rows                 : {len(raw)}"
    )

    print(
        f"Clean rows               : {len(clean)}"
    )

    print(
        f"Rows removed             : "
        f"{len(raw) - len(clean)}"
    )

    print(
        f"Notes with symptoms      : "
        f"{(clean['symptom_count'] > 0).sum()}"
    )

    print(
        f"Notes with critical      : "
        f"{clean['has_critical_symptom'].sum()}"
    )

    print(
        f"Total symptom mentions   : "
        f"{clean['symptom_count'].sum()}"
    )

    print(
        f"Total critical mentions  : "
        f"{clean['critical_symptom_count'].sum()}"
    )

    print()
    print("Transformed sample:")

    print(
        clean[
            [
                "note_id",
                "patient_id",
                "clean_note_text",
                "symptoms_found",
                "symptom_count",
                "critical_symptoms_found",
                "critical_symptom_count",
                "has_critical_symptom",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()