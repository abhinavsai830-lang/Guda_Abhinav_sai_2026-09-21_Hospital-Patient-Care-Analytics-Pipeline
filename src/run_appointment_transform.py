from src.extract import (
    extract_appointments,
    extract_patients,
)

from src.transform import (
    transform_appointments,
)


def main():

    patients = extract_patients()

    appointments = extract_appointments()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    clean = transform_appointments(
        appointments,
        valid_patient_ids,
    )

    print("=" * 70)
    print("APPOINTMENT TRANSFORMATION")
    print("=" * 70)

    print(
        f"Raw rows            : {len(appointments)}"
    )

    print(
        f"Clean rows          : {len(clean)}"
    )

    print(
        f"Rows removed        : "
        f"{len(appointments) - len(clean)}"
    )

    print(
        f"Completed visits    : "
        f"{(clean['status'] == 'Completed').sum()}"
    )

    print(
        f"No-shows            : "
        f"{(clean['status'] == 'No-Show').sum()}"
    )

    print(
        f"Cancelled           : "
        f"{(clean['status'] == 'Cancelled').sum()}"
    )

    completed = clean[
        clean["status"] == "Completed"
    ]

    print(
        f"Average wait time   : "
        f"{completed['waiting_minutes'].mean():.2f} minutes"
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