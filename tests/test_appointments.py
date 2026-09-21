from pathlib import Path

import pandas as pd

from config import SOURCE_FILES


EXPECTED_COLUMNS = {
    "appointment_id",
    "patient_id",
    "doctor_id",
    "department",
    "scheduled_time",
    "checkin_time",
    "consultation_start_time",
    "status",
}


def test_appointment_dataset_exists():
    path = Path(
        SOURCE_FILES["appointments"]
    )

    assert path.exists()


def test_appointment_dataset_has_expected_columns():
    df = pd.read_csv(
        SOURCE_FILES["appointments"]
    )

    assert EXPECTED_COLUMNS.issubset(
        set(df.columns)
    )


def test_appointment_ids_are_unique():
    df = pd.read_csv(
        SOURCE_FILES["appointments"]
    )

    assert df["appointment_id"].is_unique


def test_appointment_dataset_has_expected_size():
    df = pd.read_csv(
        SOURCE_FILES["appointments"]
    )

    assert len(df) == 1200


def test_appointment_statuses_are_valid():
    df = pd.read_csv(
        SOURCE_FILES["appointments"]
    )

    valid_statuses = {
        "Completed",
        "No-Show",
        "Cancelled",
    }

    assert set(
        df["status"].unique()
    ).issubset(valid_statuses)


def test_raw_data_contains_unknown_patients():
    """
    Unknown patients are intentional raw-data problems.
    The Transform stage will remove them later.
    """

    appointments = pd.read_csv(
        SOURCE_FILES["appointments"]
    )

    patients = pd.read_csv(
        SOURCE_FILES["patients"]
    )

    unknown_count = (
        ~appointments["patient_id"].isin(
            patients["patient_id"]
        )
    ).sum()

    assert unknown_count > 0


def test_raw_data_contains_negative_waiting_times():
    """
    Negative waiting times are intentionally generated
    as bad source data.
    """

    appointments = pd.read_csv(
        SOURCE_FILES["appointments"]
    )

    completed = appointments[
        appointments["status"] == "Completed"
    ].copy()

    completed["checkin_time"] = pd.to_datetime(
        completed["checkin_time"]
    )

    completed["consultation_start_time"] = pd.to_datetime(
        completed["consultation_start_time"]
    )

    waiting_minutes = (
        completed["consultation_start_time"]
        - completed["checkin_time"]
    ).dt.total_seconds() / 60

    assert (
        waiting_minutes < 0
    ).sum() > 0