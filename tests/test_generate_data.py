from pathlib import Path

import pandas as pd

from config import SOURCE_FILES


def test_patient_dataset_exists():
    path = Path(SOURCE_FILES["patients"])

    assert path.exists()


def test_patient_dataset_has_expected_columns():
    df = pd.read_csv(
        SOURCE_FILES["patients"]
    )

    expected_columns = {
        "patient_id",
        "name",
        "gender",
        "date_of_birth",
        "city",
        "blood_group",
        "chronic_condition",
        "registration_date",
    }

    assert expected_columns.issubset(
        set(df.columns)
    )


def test_patient_dataset_contains_duplicates():
    df = pd.read_csv(
        SOURCE_FILES["patients"]
    )

    duplicate_count = (
        df["patient_id"]
        .duplicated()
        .sum()
    )

    assert duplicate_count > 0