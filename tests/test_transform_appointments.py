import pandas as pd

from src.extract import (
    extract_appointments,
    extract_patients,
)

from src.transform import (
    transform_appointments,
)


def test_unknown_patients_are_removed():

    patients = extract_patients()

    appointments = extract_appointments()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    clean = transform_appointments(
        appointments,
        valid_patient_ids,
    )

    assert clean["patient_id"].isin(
        valid_patient_ids
    ).all()


def test_negative_waiting_times_are_removed():

    patients = extract_patients()

    appointments = extract_appointments()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    clean = transform_appointments(
        appointments,
        valid_patient_ids,
    )

    completed = clean[
        clean["status"] == "Completed"
    ]

    assert (
        completed["waiting_minutes"]
        >= 0
    ).all()


def test_waiting_time_is_created():

    patients = extract_patients()

    appointments = extract_appointments()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    clean = transform_appointments(
        appointments,
        valid_patient_ids,
    )

    assert "waiting_minutes" in clean.columns

    completed = clean[
        clean["status"] == "Completed"
    ]

    assert completed[
        "waiting_minutes"
    ].notna().all()


def test_derived_columns_are_created():

    patients = extract_patients()

    appointments = extract_appointments()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    clean = transform_appointments(
        appointments,
        valid_patient_ids,
    )

    expected_columns = {
        "appointment_date",
        "appointment_hour",
        "day_of_week",
        "is_no_show",
    }

    assert expected_columns.issubset(
        clean.columns
    )


def test_no_show_flag_is_correct():

    patients = extract_patients()

    appointments = extract_appointments()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    clean = transform_appointments(
        appointments,
        valid_patient_ids,
    )

    assert (
        clean.loc[
            clean["status"] == "No-Show",
            "is_no_show",
        ]
        == 1
    ).all()

    assert (
        clean.loc[
            clean["status"] != "No-Show",
            "is_no_show",
        ]
        == 0
    ).all()


def test_completed_waiting_time_formula():

    patients = extract_patients()

    appointments = extract_appointments()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    clean = transform_appointments(
        appointments,
        valid_patient_ids,
    )

    completed = clean[
        clean["status"] == "Completed"
    ].copy()

    expected_wait = (
        (
            completed["consultation_start_time"]
            - completed["checkin_time"]
        )
        .dt.total_seconds()
        / 60
    )

    pd.testing.assert_series_equal(
        completed[
            "waiting_minutes"
        ].reset_index(drop=True),
        expected_wait.reset_index(drop=True),
        check_names=False,
    )