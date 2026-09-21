from pathlib import Path

import pandas as pd

from config import SOURCE_FILES


EXPECTED_COLUMNS = {
    "patient_id",
    "device_id",
    "reading_time",
    "heart_rate",
    "spo2",
    "body_temp",
}


def test_wearables_dataset_exists():

    path = Path(
        SOURCE_FILES["wearables"]
    )

    assert path.exists()


def test_wearables_dataset_has_expected_columns():

    df = pd.read_csv(
        SOURCE_FILES["wearables"]
    )

    assert EXPECTED_COLUMNS.issubset(
        set(df.columns)
    )


def test_wearables_has_expected_number_of_devices():

    df = pd.read_csv(
        SOURCE_FILES["wearables"]
    )

    assert (
        df["device_id"].nunique()
        == 60
    )


def test_wearables_contains_sensor_errors():

    df = pd.read_csv(
        SOURCE_FILES["wearables"]
    )

    has_zero_heart_rate = (
        df["heart_rate"] == 0
    ).any()

    has_extreme_heart_rate = (
        df["heart_rate"] == 300
    ).any()

    has_missing_spo2 = (
        df["spo2"].isna()
    ).any()

    has_invalid_temperature = (
        df["body_temp"] == 0
    ).any()

    assert (
        has_zero_heart_rate
        or has_extreme_heart_rate
        or has_missing_spo2
        or has_invalid_temperature
    )


def test_wearables_contains_duplicate_readings():

    df = pd.read_csv(
        SOURCE_FILES["wearables"]
    )

    duplicate_count = (
        df.duplicated(
            [
                "device_id",
                "reading_time",
            ]
        ).sum()
    )

    assert duplicate_count > 0


def test_reading_times_can_be_parsed():

    df = pd.read_csv(
        SOURCE_FILES["wearables"]
    )

    reading_times = pd.to_datetime(
        df["reading_time"],
        errors="coerce",
    )

    assert reading_times.notna().all()